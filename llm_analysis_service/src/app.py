from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.configs.mongodb import mongo_settings
from src.configs.gigachat import gigachat_settings
from src.db.mongodb import (
    MongoDBClient,
    DiarizationReader,
    AnalysisRepository,
    ChatSessionRepository,
)
from src.services.chunking import ChunkingService
from src.services.llm_client import LLMClient
from src.services.analysis import AnalysisService
from src.services.chat import ChatService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и очистка зависимостей приложения.

    Startup: создаёт MongoDB-клиент, LLM-клиент, reader/repository, сервисы.
    Shutdown: закрывает HTTP-клиенты и соединения с БД.
    """
    # --- Startup ---
    mongodb_client = MongoDBClient(
        url=mongo_settings.url,
        database=mongo_settings.MONGO_DB,
    )

    llm_client = LLMClient(
        credentials=gigachat_settings.GIGACHAT_CREDENTIALS,
        model=gigachat_settings.GIGACHAT_MODEL,
        temperature=gigachat_settings.GIGACHAT_TEMPERATURE,
        max_tokens=gigachat_settings.GIGACHAT_MAX_TOKENS,
    )

    diarization_reader = DiarizationReader(client=mongodb_client)
    analysis_repo = AnalysisRepository(client=mongodb_client)
    await analysis_repo.ensure_indexes()

    chunking_service = ChunkingService()

    analysis_service = AnalysisService(
        analysis_repo=analysis_repo,
        diarization_reader=diarization_reader,
        chunking_service=chunking_service,
        llm_client=llm_client,
    )

    app.state.diarization_reader = diarization_reader
    app.state.analysis_service = analysis_service

    chat_repo = ChatSessionRepository(client=mongodb_client)
    await chat_repo.ensure_indexes()

    chat_service = ChatService(
        chat_repo=chat_repo,
        diarization_reader=diarization_reader,
        chunking_service=chunking_service,
        llm_client=llm_client,
    )

    app.state.chat_service = chat_service

    yield

    # --- Shutdown ---
    await llm_client.close()
    await mongodb_client.close()
