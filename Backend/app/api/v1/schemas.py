from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class Statement(BaseModel):
    speaker: str
    text: str
    round: int

class DebateTurnRequest(BaseModel):
    model_a: str
    model_b: str
    current_turn: str                 # which model should speak now (must equal model_a or model_b)
    original_debate_topic: str
    previous_conversation: Optional[List[Statement]] = []
    current_round: int = 1
    max_rounds: int = 3

class DebateTurnResponse(BaseModel):
    next_turn: str
    current_round: int
    done: bool
    updated_conversation: List[Statement]
    message: Optional[str] = None

class SessionCreateRequest(BaseModel):
    model_a: str
    model_b: str
    starting_turn: str
    original_debate_topic: str
    max_rounds: int = 3

class SessionCreateResponse(BaseModel):
    session_id: UUID
    state: DebateTurnResponse

class SessionStateResponse(BaseModel):
    session_id: UUID
    model_a: str
    model_b: str
    current_turn: str
    current_round: int
    max_rounds: int
    done: bool
    transcript: List[Statement]