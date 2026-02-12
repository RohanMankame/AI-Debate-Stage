from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.api.v1 import schemas as s
from app.api.services.debate_manager import get_debate_manager, DebateManager

router = APIRouter()

@router.post("/debate/turn", response_model=s.DebateTurnResponse)
async def debate_turn(req: s.DebateTurnRequest, manager: DebateManager = Depends(get_debate_manager)):
    try:
        resp = await manager.handle_turn(
            model_a=req.model_a,
            model_b=req.model_b,
            current_turn=req.current_turn,
            topic=req.original_debate_topic,
            previous_conversation=req.previous_conversation or [],
            current_round=req.current_round,
            max_rounds=req.max_rounds,
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/debate/session", response_model=s.SessionCreateResponse)
async def create_session(req: s.SessionCreateRequest, manager: DebateManager = Depends(get_debate_manager)):
    try:
        session_id, state = manager.create_session(
            model_a=req.model_a,
            model_b=req.model_b,
            starting_turn=req.starting_turn,
            topic=req.original_debate_topic,
            max_rounds=req.max_rounds,
            model_a_model=req.model_a_model,
            model_b_model=req.model_b_model,
            model_a_stance=req.model_a_stance,
            model_b_stance=req.model_b_stance,
        )
        return s.SessionCreateResponse(session_id=session_id, state=state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/debate/session/{session_id}/advance", response_model=s.DebateTurnResponse)
async def advance_session(session_id: UUID, manager: DebateManager = Depends(get_debate_manager)):
    try:
        return await manager.advance_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/debate/session/{session_id}", response_model=s.SessionStateResponse)
async def get_session(session_id: UUID, manager: DebateManager = Depends(get_debate_manager)):
    try:
        return manager.get_session_state(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session not found")