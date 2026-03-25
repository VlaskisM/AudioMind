from fastapi import Request

from src.db.mongodb.diarization_reader import DiarizationReader
from src.services.analysis import AnalysisService
from src.services.chat import ChatService


def get_analysis_service(request: Request) -> AnalysisService:
    """Dependency для получения AnalysisService из app.state."""
    return request.app.state.analysis_service


def get_chat_service(request: Request) -> ChatService:
    """Dependency для получения ChatService из app.state."""
    return request.app.state.chat_service


def get_diarization_reader(request: Request) -> DiarizationReader:
    """Dependency для получения DiarizationReader из app.state."""
    return request.app.state.diarization_reader
