from typing import List
from app.api.v1.schemas import Statement
from pydantic import BaseModel

class DebateManager:
    async def run_debate(self, topic: str, model_a: str, model_b: str, rounds: int = 3) -> List[Statement]:
        # Mock implementation: alternate simple statements.
        transcript: List[Statement] = []
        for r in range(1, rounds + 1):
            transcript.append(Statement(speaker=model_a, text=f"{model_a} argues on '{topic}' (round {r})", round=r))
            transcript.append(Statement(speaker=model_b, text=f"{model_b} rebuts on '{topic}' (round {r})", round=r))
        return transcript

# Dependency injector factory (simple). Replace with DI framework if desired.
def get_debate_manager() -> DebateManager:
    return DebateManager()