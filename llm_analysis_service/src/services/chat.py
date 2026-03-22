from datetime import datetime, timezone

from llm_analysis_service.src.db.mongodb.chat_session_repository import ChatSessionRepository
from llm_analysis_service.src.db.mongodb.diarization_reader import DiarizationReader
from llm_analysis_service.src.services.analysis import AnalysisError
from llm_analysis_service.src.services.chunking import ChunkingService
from llm_analysis_service.src.services.llm_client import LLMClient
from llm_analysis_service.src.services.models import ChatAnswer
from llm_analysis_service.src.services.prompts import CHAT_SYSTEM_PROMPT


class ChatService:
    """Оркестрация чата по транскрипции: загрузка данных, token budget, LLM, история."""

    MODEL_CONTEXT_LIMIT = 128_000
    RESPONSE_RESERVE = 4_096

    def __init__(
        self,
        chat_repo: ChatSessionRepository,
        diarization_reader: DiarizationReader,
        chunking_service: ChunkingService,
        llm_client: LLMClient,
    ) -> None:
        self._chat_repo = chat_repo
        self._diarization = diarization_reader
        self._chunking = chunking_service
        self._llm = llm_client

    async def ask(self, recording_id: int, question: str) -> ChatAnswer:
        """Полный pipeline: транскрипция -> история -> token budget -> LLM -> сохранение."""
        # 1. Загрузить транскрипцию (диаризация) и отформатировать
        transcript_text = await self._load_transcript(recording_id)

        # 2. Загрузить историю из MongoDB
        history = await self._chat_repo.get_history(recording_id)

        # 3. Собрать messages с token budget
        messages = self._build_messages(transcript_text, history, question)

        # 4. Вызвать LLM
        result: ChatAnswer = await self._llm.chat_structured(messages, ChatAnswer)  # type: ignore[assignment]

        # 5. Сохранить user question + assistant answer в историю
        now = datetime.now(timezone.utc).isoformat()
        await self._chat_repo.append_messages(recording_id, [
            {"role": "user", "content": question, "timestamp": now},
            {"role": "assistant", "content": result.model_dump_json(), "timestamp": now},
        ])

        # 6. Вернуть ChatAnswer
        return result

    async def get_history(self, recording_id: int) -> list[dict]:
        """Для GET endpoint -- проксирует к repository."""
        return await self._chat_repo.get_history(recording_id)

    async def delete_session(self, recording_id: int) -> bool:
        """Для DELETE endpoint -- проксирует к repository."""
        return await self._chat_repo.delete_session(recording_id)

    async def _load_transcript(self, recording_id: int) -> str:
        """Загрузить диаризацию и отформатировать в текст."""
        speakers = await self._diarization.get_speakers(recording_id)
        if not speakers:
            raise AnalysisError(
                f"Diarization data not found for recording_id={recording_id}"
            )
        return self._format_transcript(speakers)

    def _format_transcript(self, speakers: list[dict]) -> str:
        """Flatten + sort по start time, форматировать через LLMClient._format_chunk."""
        turns = sorted(
            (
                {"speaker": sp["label"], "text": seg["text"], "start": seg["start"], "end": seg["end"]}
                for sp in speakers
                for seg in sp.get("segments", ())
            ),
            key=lambda t: t["start"],
        )
        return LLMClient._format_chunk(turns)

    def _build_messages(
        self,
        transcript_text: str,
        history: list[dict],
        user_question: str,
    ) -> list[dict]:
        """Собрать messages array с token budget management.

        Приоритеты: system prompt + транскрипция > последний вопрос > история (от новых к старым).
        """
        enc = self._chunking._enc
        budget = self.MODEL_CONTEXT_LIMIT - self.RESPONSE_RESERVE

        # System message включает промпт + транскрипцию
        system_content = (
            CHAT_SYSTEM_PROMPT
            + "\n\n<transcript>\n"
            + transcript_text
            + "\n</transcript>"
        )
        system_tokens = len(enc.encode(system_content))
        question_tokens = len(enc.encode(user_question))

        remaining = budget - system_tokens - question_tokens

        # Итерируем историю от новых к старым, добавляем пока влезает
        trimmed_history: list[dict] = []
        for msg in reversed(history):
            msg_tokens = len(enc.encode(msg["content"]))
            if remaining - msg_tokens < 0:
                break
            remaining -= msg_tokens
            # Без timestamp -- OpenAI API не принимает лишние поля
            trimmed_history.append({"role": msg["role"], "content": msg["content"]})

        # Восстанавливаем хронологический порядок
        trimmed_history.reverse()

        return (
            [{"role": "system", "content": system_content}]
            + trimmed_history
            + [{"role": "user", "content": user_question}]
        )
