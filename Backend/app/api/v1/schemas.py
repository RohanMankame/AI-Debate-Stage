from pydantic import BaseModel
from typing import List

class DebateRequest(BaseModel):
    topic: str
    model_a: str = "model-a"
    model_b: str = "model-b"
    rounds: int = 3

class Statement(BaseModel):
    speaker: str
    text: str
    round: int

class DebateResponse(BaseModel):
    topic: str
    transcript: List[Statement]