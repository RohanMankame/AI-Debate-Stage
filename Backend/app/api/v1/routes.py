from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.schemas import DebateRequest, DebateResponse
from app.api.services.debate_manager import get_debate_manager, DebateManager

router = APIRouter()

@router.post("/debate", response_model=DebateResponse)
async def start_debate(req: DebateRequest, manager: DebateManager = Depends(get_debate_manager)):
    """
    Start a debate between two AI models on a topic.
    Currently returns a mocked turn-by-turn result; replace with model integrations.
    """
    try:
        result = await manager.run_debate(req.topic, req.model_a, req.model_b, req.rounds)
        return DebateResponse(topic=req.topic, transcript=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))