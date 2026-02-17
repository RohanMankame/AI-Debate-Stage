from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID

class Statement(BaseModel):
    speaker: str
    text: str
    round: int

class DebateTurnRequest(BaseModel):
    model_a: str
    model_b: str
    current_turn: str
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
    model_a_model: Optional[str] = "gpt-3.5-turbo"
    model_b_model: Optional[str] = "gpt-3.5-turbo"
    model_a_stance: Optional[str] = "Argue in favor"
    model_b_stance: Optional[str] = "Argue against"
    # Judge fields
    judge_name: Optional[str] = "Judge"
    judge_model: Optional[str] = "JudgeAI"
    judge_model_model: Optional[str] = "gpt-4"
    judge_instructions: Optional[str] = "Read the full debate transcript and decide the winner based on the strength of arguments and persuasiveness."

class SessionCreateResponse(BaseModel):
    session_id: UUID
    state: DebateTurnResponse

class SessionStateResponse(BaseModel):
    session_id: UUID
    model_a: str
    model_b: str
    model_a_model: str
    model_b_model: str
    model_a_stance: Optional[str]
    model_b_stance: Optional[str]
    judge_name: Optional[str]
    judge_model: Optional[str]
    judge_model_model: Optional[str]
    judge_instructions: Optional[str]
    current_turn: str
    current_round: int
    max_rounds: int
    done: bool
    transcript: List[Statement]

class JudgeResponse(BaseModel):
    winner: Optional[str]
    reasoning: str
    scores: Optional[Dict[str, float]] = None