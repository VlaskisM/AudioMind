from pydantic import BaseModel

from llm_analysis_service.src.db.mongodb.analysis_repository import AnalysisRepository
from llm_analysis_service.src.db.mongodb.diarization_reader import DiarizationReader
from llm_analysis_service.src.services.chunking import ChunkingService
from llm_analysis_service.src.services.llm_client import LLMClient
from llm_analysis_service.src.services.models import (
    SummaryResult,
    KeyPointsResult,
    ActionItemsResult,
    FaqResult,
)
from llm_analysis_service.src.services.prompts import (
    SUMMARY_MAP_PROMPT,
    SUMMARY_REDUCE_PROMPT,
    KEY_POINTS_MAP_PROMPT,
    KEY_POINTS_REDUCE_PROMPT,
    ACTION_ITEMS_MAP_PROMPT,
    ACTION_ITEMS_REDUCE_PROMPT,
    FAQ_MAP_PROMPT,
    FAQ_REDUCE_PROMPT,
)


class AnalysisError(Exception):
    """Ошибка анализа (нет данных, LLM отказал, etc.)."""

    pass


class AnalysisService:
    """Оркестрация полного pipeline анализа: кэш -> данные -> chunking -> LLM -> сохранение."""

    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        diarization_reader: DiarizationReader,
        chunking_service: ChunkingService,
        llm_client: LLMClient,
    ) -> None:
        self._repo = analysis_repo
        self._diarization = diarization_reader
        self._chunking = chunking_service
        self._llm = llm_client

    async def get_summary(self, recording_id: int) -> SummaryResult:
        """Получить краткое содержание записи."""
        result = await self._run_analysis(
            recording_id=recording_id,
            analysis_type="summary",
            map_prompt=SUMMARY_MAP_PROMPT,
            reduce_prompt=SUMMARY_REDUCE_PROMPT,
            result_type=SummaryResult,
        )
        return result  # type: ignore[return-value]

    async def get_key_points(self, recording_id: int) -> KeyPointsResult:
        """Получить ключевые тезисы записи с привязкой к спикерам."""
        result = await self._run_analysis(
            recording_id=recording_id,
            analysis_type="key_points",
            map_prompt=KEY_POINTS_MAP_PROMPT,
            reduce_prompt=KEY_POINTS_REDUCE_PROMPT,
            result_type=KeyPointsResult,
        )
        return result  # type: ignore[return-value]

    async def get_action_items(self, recording_id: int) -> ActionItemsResult:
        """Получить action items записи с ответственными."""
        result = await self._run_analysis(
            recording_id=recording_id,
            analysis_type="action_items",
            map_prompt=ACTION_ITEMS_MAP_PROMPT,
            reduce_prompt=ACTION_ITEMS_REDUCE_PROMPT,
            result_type=ActionItemsResult,
        )
        return result  # type: ignore[return-value]

    async def get_faq(self, recording_id: int) -> FaqResult:
        """Получить FAQ по содержанию записи."""
        result = await self._run_analysis(
            recording_id=recording_id,
            analysis_type="faq",
            map_prompt=FAQ_MAP_PROMPT,
            reduce_prompt=FAQ_REDUCE_PROMPT,
            result_type=FaqResult,
        )
        return result  # type: ignore[return-value]

    async def _run_analysis(
        self,
        recording_id: int,
        analysis_type: str,
        map_prompt: str,
        reduce_prompt: str,
        result_type: type[BaseModel],
    ) -> BaseModel:
        """Общий pipeline анализа для всех типов.

        1. Проверить кэш
        2. Получить данные диаризации
        3. Разбить на чанки
        4. Map-reduce через LLM
        5. Сохранить результат в кэш
        """
        # 1. Проверить кэш
        cached = await self._repo.get_cached(recording_id, analysis_type)
        if cached is not None:
            return result_type.model_validate(cached["result"])

        # 2. Получить данные диаризации
        speakers = await self._diarization.get_speakers(recording_id)
        if not speakers:
            raise AnalysisError(
                f"Diarization data not found for recording_id={recording_id}"
            )

        # 3. Chunking
        chunks = self._chunking.chunk_by_speakers(speakers)

        # 4. LLM map-reduce
        result = await self._llm.map_reduce_structured(
            chunks=chunks,
            map_prompt=map_prompt,
            reduce_prompt=reduce_prompt,
            result_type=result_type,
        )

        # 5. Сохранить в кэш
        await self._repo.save(
            recording_id=recording_id,
            analysis_type=analysis_type,
            result=result.model_dump(),
            model=self._llm.model,
        )

        return result
