from typing import List, Dict, Tuple, Optional
from uuid import uuid4, UUID
from app.api.v1.schemas import Statement, DebateTurnResponse, JudgeResponse
import copy
from app.api.services.llm_client import get_llm_client

# Allowed models (expand as needed)
ALLOWED_MODELS = {
    "gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-3.5-turbo-0613",
    "gemini-2.0-flash", "gemini-1.5", "text-bison-001"
}

class DebateManager:
    def __init__(self):
        self._sessions: Dict[UUID, Dict] = {}
        self._llm = get_llm_client()

    async def _call_model(self, model_name: str, role_hint: str, topic: str, recent_statements: List[Statement]) -> str:
        messages = [
            {"role": "system", "content": role_hint},
            {"role": "user", "content": f"Topic: {topic}"},
        ]
        if recent_statements:
            # include the transcript lines
            for s in recent_statements:
                messages.append({"role": "user", "content": f"{s.speaker}: {s.text}"})
        messages.append({"role": "user", "content": "Produce one concise debate turn (one or two sentences)."})
        return await self._llm.generate(model=model_name, messages=messages, temperature=0.7, max_tokens=512)

    # --- existing handle_turn / create_session / advance_session / get_session_state methods ---
    # (keep your current implementations, but ensure create_session stores judge fields)
    # Below are the create_session, advance_session, get_session_state and new evaluate_session implementations.

    def create_session(
        self,
        model_a: str,
        model_b: str,
        starting_turn: str,
        topic: str,
        max_rounds: int,
        model_a_model: str = "gpt-3.5-turbo",
        model_b_model: str = "gpt-3.5-turbo",
        model_a_stance: Optional[str] = "Argue in favor",
        model_b_stance: Optional[str] = "Argue against",
        judge_name: Optional[str] = "Judge",
        judge_model: Optional[str] = "JudgeAI",
        judge_model_model: Optional[str] = "gpt-4",
        judge_instructions: Optional[str] = "Read the full debate transcript and decide the winner based on strength of arguments and persuasiveness."
    ) -> Tuple[UUID, DebateTurnResponse]:
        if starting_turn not in (model_a, model_b):
            raise ValueError("starting_turn must be model_a or model_b")
        if model_a_model not in ALLOWED_MODELS or model_b_model not in ALLOWED_MODELS or judge_model_model not in ALLOWED_MODELS:
            raise ValueError(f"model must be one of: {sorted(ALLOWED_MODELS)}")

        session_id = uuid4()
        session = {
            "model_a": model_a,
            "model_b": model_b,
            "model_a_model": model_a_model,
            "model_b_model": model_b_model,
            "model_a_stance": model_a_stance,
            "model_b_stance": model_b_stance,
            "judge_name": judge_name,
            "judge_model": judge_model,
            "judge_model_model": judge_model_model,
            "judge_instructions": judge_instructions,
            "topic": topic,
            "current_turn": starting_turn,
            "current_round": 1,
            "max_rounds": max_rounds,
            "transcript": [],
            "done": False,
        }
        self._sessions[session_id] = session
        initial_state = DebateTurnResponse(
            next_turn=starting_turn,
            current_round=1,
            done=False,
            updated_conversation=[],
            message="session created"
        )
        return session_id, initial_state

    # (reuse your existing advance_session implementation but ensure it persists judge fields - unchanged here)
    async def advance_session(self, session_id: UUID) -> DebateTurnResponse:
        session = self._sessions[session_id]
        if session["done"]:
            return DebateTurnResponse(
                next_turn=session["current_turn"],
                current_round=session["current_round"],
                done=True,
                updated_conversation=session["transcript"],
                message="session already done"
            )

        # existing logic: pick current_turn, model_name from session and call _call_model...
        model_a = session["model_a"]
        model_b = session["model_b"]
        current_turn = session["current_turn"]
        topic = session["topic"]
        current_round = session["current_round"]
        max_rounds = session["max_rounds"]
        transcript = [s for s in session["transcript"] if s.speaker != "__system_hint__"]

        if current_turn == model_a:
            model_name = session.get("model_a_model", "gpt-3.5-turbo")
            stance = session.get("model_a_stance", "Argue in favor")
        else:
            model_name = session.get("model_b_model", "gpt-3.5-turbo")
            stance = session.get("model_b_stance", "Argue against")

        opponent = model_a if current_turn == model_b else model_b
        opponent_latest = ""
        for s in reversed(transcript):
            if s.speaker != "__system_hint__":
                opponent_latest = s.text
                break

        if opponent_latest:
            role_hint = (
                f"You are {current_turn}. You must argue the following stance: {stance}. "
                f"Respond to {opponent}'s latest: \"{opponent_latest}\". Do not concede; defend or rebut while staying on stance."
            )
        else:
            role_hint = (
                f"You are {current_turn}. You must argue the following stance: {stance}. "
                f"Open the debate on '{topic}' with one concise, persuasive point that supports your stance."
            )

        generated = await self._call_model(model_name=model_name, role_hint=role_hint, topic=topic, recent_statements=transcript)
        new_text = f"(round {current_round}){current_turn}: {generated}"
        new_stmt = Statement(speaker=current_turn, text=new_text, round=current_round)
        transcript.append(new_stmt)

        other = model_a if current_turn == model_b else model_b
        next_turn = other
        next_round = current_round + 1 if current_turn == model_b else current_round
        done = (current_turn == model_b and current_round >= max_rounds)

        hint_text = (
            f"[You are {next_turn}] You must argue the following stance: {session.get('model_a_stance') if next_turn==model_a else session.get('model_b_stance')}. "
            f"Respond to: \"{new_text}\". Be concise and persuasive."
        )
        hint_stmt = Statement(speaker="__system_hint__", text=hint_text, round=next_round)
        transcript.append(hint_stmt)

        session["transcript"] = transcript
        session["current_turn"] = next_turn
        session["current_round"] = next_round
        if done:
            session["done"] = True

        return DebateTurnResponse(
            next_turn=next_turn,
            current_round=next_round,
            done=done,
            updated_conversation=transcript,
            message=f"Processed turn for {current_turn}"
        )

    def get_session_state(self, session_id: UUID):
        session = self._sessions[session_id]
        return {
            "session_id": session_id,
            "model_a": session["model_a"],
            "model_b": session["model_b"],
            "model_a_model": session["model_a_model"],
            "model_b_model": session["model_b_model"],
            "model_a_stance": session.get("model_a_stance"),
            "model_b_stance": session.get("model_b_stance"),
            "judge_name": session.get("judge_name"),
            "judge_model": session.get("judge_model"),
            "judge_model_model": session.get("judge_model_model"),
            "judge_instructions": session.get("judge_instructions"),
            "current_turn": session["current_turn"],
            "current_round": session["current_round"],
            "max_rounds": session["max_rounds"],
            "done": session["done"],
            "transcript": session["transcript"],
        }

    # --- New: evaluate_session (judge)
    async def evaluate_session(self, session_id: UUID) -> JudgeResponse:
        session = self._sessions[session_id]
        transcript = [s for s in session["transcript"] if s.speaker != "__system_hint__"]
        topic = session["topic"]
        model_a = session["model_a"]
        model_b = session["model_b"]

        judge_model_name = session.get("judge_model_model", "gpt-4")
        judge_instructions = session.get("judge_instructions", "Read the full debate transcript and decide the winner based on strength of arguments and persuasiveness.")

        # Build role hint with explicit tasks for judge
        role_hint = (
            f"You are the judge. {judge_instructions} "
            f"Return output with a single-line 'Winner: <{model_a}|{model_b}|Tie>' then 'Reasoning:' followed by a short justification."
        )

        # Build messages: include stances and the transcript
        messages = [
            {"role": "system", "content": role_hint},
            {"role": "user", "content": f"Topic: {topic}"},
            {"role": "user", "content": f"{model_a} stance: {session.get('model_a_stance')}"},
            {"role": "user", "content": f"{model_b} stance: {session.get('model_b_stance')}"},
            {"role": "user", "content": "Transcript:"}
        ]
        for s in transcript:
            messages.append({"role": "user", "content": f"{s.speaker}: {s.text}"})

        messages.append({"role": "user", "content": "Decide the winner."})

        generated = await self._llm.generate(model=judge_model_name, messages=messages, temperature=0.0, max_tokens=512)
        # naive parse: look for 'Winner:' then remainder as reasoning
        winner = None
        reasoning = generated
        lower = generated.lower()
        if "winner:" in lower:
            try:
                # find 'winner:' index case-insensitive
                idx = lower.index("winner:")
                after = generated[idx + len("winner:"):].strip()
                # split by newline
                parts = after.splitlines()
                first = parts[0].strip()
                # first token could be 'ModelA' or 'ModelB' or 'Tie'
                tok = first.split()[0].strip().strip(":").strip()
                winner = tok
                reasoning = "\n".join(parts[1:]).strip() if len(parts) > 1 else generated
            except Exception:
                winner = None
                reasoning = generated

        return JudgeResponse(winner=winner, reasoning=reasoning, scores=None)

# dependency factory
_singleton = DebateManager()
def get_debate_manager() -> DebateManager:
    return _singleton