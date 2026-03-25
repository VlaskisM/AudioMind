from pydantic import BaseModel

from src.services.models import ChatAnswer


class ChatRequest(BaseModel):
    """Request schema для POST /analysis/{recording_id}/chat."""

    question: str  # Вопрос пользователя


class ChatResponse(BaseModel):
    """Response schema для POST /analysis/{recording_id}/chat."""

    status: str
    data: ChatAnswer


class ChatHistoryResponse(BaseModel):
    """Response schema для GET /analysis/{recording_id}/chat/history."""

    status: str
    data: list[dict]  # Массив сообщений {role, content, timestamp}
