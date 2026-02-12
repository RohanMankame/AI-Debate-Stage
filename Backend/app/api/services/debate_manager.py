from typing import List, Dict, Tuple, Optional
from uuid import uuid4, UUID
from app.api.v1.schemas import Statement, DebateTurnResponse
import copy
from app.api.services.llm_client import get_llm_client

# Allowed models (GPT + Gemini/Bison names). Expand as needed.
ALLOWED_MODELS = {
    "gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-3.5-turbo-0613",
    "gemini-3-flash-preview", "gemini-2.5-flash-lite", "gemini-3-pro", "gemini-ultra", "text-bison-001"
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
            for s in recent_statements[-4:]:
                messages.append({"role": "user", "content": f"{s.speaker}: {s.text}"})
        messages.append({"role": "user", "content": "Produce one concise debate turn (one or two sentences)."})
        return await self._llm.generate(model=model_name, messages=messages, temperature=0.7, max_tokens=256)

    async def handle_turn(
        self,
        model_a: str,
        model_b: str,
        current_turn: str,
        topic: str,
        previous_conversation: List[Statement],
        current_round: int,
        max_rounds: int,
    ) -> DebateTurnResponse:
        if current_turn not in (model_a, model_b):
            raise ValueError("current_turn must be either model_a or model_b")

        transcript = [s for s in previous_conversation if s.speaker != "__system_hint__"]
        role_hint = f"You are {current_turn}. Respond concisely to the opponent."
        model_name = "gpt-3.5-turbo"
        generated = await self._call_model(model_name=model_name, role_hint=role_hint, topic=topic, recent_statements=transcript)
        new_text = f"(round {current_round}){current_turn}: {generated}"
        new_stmt = Statement(speaker=current_turn, text=new_text, round=current_round)
        transcript.append(new_stmt)

        other = model_a if current_turn == model_b else model_b
        next_turn = other
        next_round = current_round + 1 if current_turn == model_b else current_round
        done = (current_turn == model_b and current_round >= max_rounds)

        hint_text = f"[You are {next_turn}] Respond to: \"{new_text}\". Be concise."
        hint_stmt = Statement(speaker="__system_hint__", text=hint_text, round=next_round)
        transcript.append(hint_stmt)

        return DebateTurnResponse(
            next_turn=next_turn,
            current_round=next_round,
            done=done,
            updated_conversation=transcript,
            message=f"Processed turn for {current_turn}"
        )

    # --- Stateful session helpers ---

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
    ) -> Tuple[UUID, DebateTurnResponse]:
        if starting_turn not in (model_a, model_b):
            raise ValueError("starting_turn must be model_a or model_b")
        if model_a_model not in ALLOWED_MODELS or model_b_model not in ALLOWED_MODELS:
            raise ValueError(f"model must be one of: {sorted(ALLOWED_MODELS)}")

        session_id = uuid4()
        session = {
            "model_a": model_a,
            "model_b": model_b,
            "model_a_model": model_a_model,
            "model_b_model": model_b_model,
            "model_a_stance": model_a_stance,
            "model_b_stance": model_b_stance,
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

        model_a = session["model_a"]
        model_b = session["model_b"]
        current_turn = session["current_turn"]
        topic = session["topic"]
        current_round = session["current_round"]
        max_rounds = session["max_rounds"]
        transcript = [s for s in session["transcript"] if s.speaker != "__system_hint__"]

        # Select model name and stance for the speaker
        if current_turn == model_a:
            model_name = session.get("model_a_model", "gpt-3.5-turbo")
            stance = session.get("model_a_stance", "Argue in favor")
        else:
            model_name = session.get("model_b_model", "gpt-3.5-turbo")
            stance = session.get("model_b_stance", "Argue against")

        # Determine opponent latest statement (if any)
        opponent = model_a if current_turn == model_b else model_b
        opponent_latest = ""
        for s in reversed(transcript):
            if s.speaker != "__system_hint__":
                opponent_latest = s.text
                break

        # Build role hint enforcing stance
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

        # Call the selected model
        generated = await self._call_model(model_name=model_name, role_hint=role_hint, topic=topic, recent_statements=transcript)
        new_text = f"(round {current_round}){current_turn}: {generated}"
        new_stmt = Statement(speaker=current_turn, text=new_text, round=current_round)
        transcript.append(new_stmt)

        # Update session turn/round/done
        other = model_a if current_turn == model_b else model_b
        next_turn = other
        next_round = current_round + 1 if current_turn == model_b else current_round
        done = (current_turn == model_b and current_round >= max_rounds)

        # Single latest hint for next speaker
        hint_text = (
            f"[You are {next_turn}] You must argue the following stance: {session.get('model_a_stance') if next_turn==model_a else session.get('model_b_stance')}. "
            f"Respond to: \"{new_text}\". Be concise and persuasive."
        )
        hint_stmt = Statement(speaker="__system_hint__", text=hint_text, round=next_round)
        transcript.append(hint_stmt)

        # Persist updates
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
            "current_turn": session["current_turn"],
            "current_round": session["current_round"],
            "max_rounds": session["max_rounds"],
            "done": session["done"],
            "transcript": session["transcript"],
        }

# dependency factory (singleton for dev)
_singleton = DebateManager()
def get_debate_manager() -> DebateManager:
    return _singleton