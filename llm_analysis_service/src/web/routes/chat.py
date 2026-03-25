from fastapi import APIRouter, Depends, HTTPException

from src.services.analysis import AnalysisError
from src.services.chat import ChatService
from src.web.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
)
from src.web.schemas.common import BaseResponse
from src.web.dependencies import get_chat_service

router = APIRouter(prefix="/analysis", tags=["chat"])


@router.post("/{recording_id}/chat", response_model=ChatResponse)
async def ask_chat(
    recording_id: int,
    body: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Задать вопрос по транскрипции записи."""
    try:
        result = await service.ask(recording_id, body.question)
        return ChatResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{recording_id}/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    recording_id: int,
    service: ChatService = Depends(get_chat_service),
) -> ChatHistoryResponse:
    """Получить историю сообщений чата для записи."""
    history = await service.get_history(recording_id)
    return ChatHistoryResponse(status="ok", data=history)


@router.delete("/{recording_id}/chat", response_model=BaseResponse)
async def delete_chat(
    recording_id: int,
    service: ChatService = Depends(get_chat_service),
) -> BaseResponse:
    """Сбросить историю чата для записи."""
    deleted = await service.delete_session(recording_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return BaseResponse(status="ok", message="Chat session deleted")
