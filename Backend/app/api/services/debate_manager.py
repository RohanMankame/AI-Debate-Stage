from typing import List, Dict, Tuple
from uuid import uuid4, UUID
from app.api.v1.schemas import Statement, DebateTurnResponse
import copy

class DebateManager:
    def __init__(self):
        # session_id (UUID) -> session dict
        self._sessions: Dict[UUID, Dict] = {}

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

        transcript = list(previous_conversation)
        # Create the new statement
        recent_summary = ""
        if transcript:
            recent = transcript[-2:]
            recent_summary = " | Recent: " + " ; ".join(f"{s.speaker}: {s.text}" for s in recent)

        new_text = f"{current_turn} (round {current_round}) speaks on '{topic}'.{recent_summary}"
        new_stmt = Statement(speaker=current_turn, text=new_text, round=current_round)
        transcript.append(new_stmt)

        other = model_a if current_turn == model_b else model_b
        next_turn = other
        next_round = current_round + 1 if current_turn == model_b else current_round
        done = (current_turn == model_b and current_round >= max_rounds)

        # System hint for next speaker so the next request can include it in previous_conversation
        hint_text = f"[role_hint] You are {next_turn}. Continue from your previous points."
        hint_stmt = Statement(speaker="__system_hint__", text=hint_text, round=next_round)
        transcript.append(hint_stmt)

        return DebateTurnResponse(
            next_turn=next_turn,
            current_round=next_round,
            done=done,
            updated_conversation=transcript,
            message=f"Processed turn for {current_turn}"
        )

    # Session helpers
    def create_session(self, model_a: str, model_b: str, starting_turn: str, topic: str, max_rounds: int) -> Tuple[UUID, DebateTurnResponse]:
        if starting_turn not in (model_a, model_b):
            raise ValueError("starting_turn must be model_a or model_b")
        session_id = uuid4()
        session = {
            "model_a": model_a,
            "model_b": model_b,
            "topic": topic,
            "current_turn": starting_turn,
            "current_round": 1,
            "max_rounds": max_rounds,
            "transcript": [],
            "done": False,
        }
        self._sessions[session_id] = session
        # Return initial state (no new statement yet) to client
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

        # Prepare inputs for handle_turn
        resp = await self.handle_turn(
            model_a=session["model_a"],
            model_b=session["model_b"],
            current_turn=session["current_turn"],
            topic=session["topic"],
            previous_conversation=copy.deepcopy(session["transcript"]),
            current_round=session["current_round"],
            max_rounds=session["max_rounds"]
        )

        # Update session state based on response
        session["transcript"] = resp.updated_conversation
        session["current_turn"] = resp.next_turn
        session["current_round"] = resp.current_round
        if resp.done:
            session["done"] = True

        return resp

    def get_session_state(self, session_id: UUID):
        session = self._sessions[session_id]
        return {
            "session_id": session_id,
            "model_a": session["model_a"],
            "model_b": session["model_b"],
            "current_turn": session["current_turn"],
            "current_round": session["current_round"],
            "max_rounds": session["max_rounds"],
            "done": session["done"],
            "transcript": session["transcript"],
        }

# dependency factory
_singleton = DebateManager()
def get_debate_manager() -> DebateManager:
    return _singleton