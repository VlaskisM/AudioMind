from fastapi import Request

from llm_analysis_service.src.services.analysis import AnalysisService
from llm_analysis_service.src.services.chat import ChatService


def get_analysis_service(request: Request) -> AnalysisService:
    """Dependency для получения AnalysisService из app.state."""
    return request.app.state.analysis_service


def get_chat_service(request: Request) -> ChatService:
    """Dependency для получения ChatService из app.state."""
    return request.app.state.chat_service
