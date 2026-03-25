import json

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from pydantic import BaseModel


class LLMClient:
    """Обёртка над GigaChat с поддержкой map-reduce для длинных транскрипций."""

    def __init__(
        self,
        credentials: str,
        model: str = "GigaChat",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> None:
        self._client = GigaChat(
            credentials=credentials,
            model=model,
            verify_ssl_certs=False,
        )
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def model(self) -> str:
        """Имя модели (нужно для записи в кэш)."""
        return self._model

    async def complete(self, system_prompt: str, user_content: str) -> str:
        """Один вызов LLM. Возвращает текстовый ответ."""
        response = await self._client.achat(
            Chat(
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                messages=[
                    Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                    Messages(role=MessagesRole.USER, content=user_content),
                ],
            )
        )
        return response.choices[0].message.content or ""

    async def map_reduce(
        self,
        chunks: list[list[dict]],
        map_prompt: str,
        reduce_prompt: str,
    ) -> str:
        """
        Map-reduce обработка чанков транскрипции.

        Map phase:
        - Каждый чанк форматируется как текст с speaker labels
        - Добавляется контекст: "Часть N из M"
        - Running summary предыдущих чанков (2-3 предложения) передаётся в промпт
        - Вызов complete() для каждого чанка

        Reduce phase:
        - Если один чанк -- вернуть результат напрямую (без reduce)
        - Если несколько -- объединить промежуточные результаты через финальный вызов LLM
        """
        total = len(chunks)

        # Один чанк -- обрабатываем напрямую без map-reduce
        if total == 1:
            formatted = self._format_chunk(chunks[0])
            return await self.complete(map_prompt, formatted)

        # Map phase: обработка каждого чанка с running summary
        partial_results: list[str] = []
        running_summary = ""

        for i, chunk in enumerate(chunks, start=1):
            formatted = self._format_chunk(chunk)

            # Формируем контекст для текущего чанка
            context_parts = [f"Часть {i} из {total}."]
            if running_summary:
                context_parts.append(f"Краткое содержание предыдущих частей: {running_summary}")
            context = "\n".join(context_parts)

            user_content = f"{context}\n\n{formatted}"
            result = await self.complete(map_prompt, user_content)
            partial_results.append(result)

            # Генерируем running summary для следующего чанка (2-3 предложения)
            if i < total:
                summary_prompt = (
                    "Сформулируй краткое содержание следующего текста в 2-3 предложениях. "
                    "Сохрани ключевые темы и упомянутых спикеров."
                )
                running_summary = await self.complete(summary_prompt, result)

        # Reduce phase: объединение промежуточных результатов
        combined = "\n\n---\n\n".join(
            f"Часть {i}: {r}" for i, r in enumerate(partial_results, start=1)
        )
        return await self.complete(reduce_prompt, combined)

    @staticmethod
    def _format_chunk(chunk: list[dict]) -> str:
        """
        Форматирует чанк в текст для промпта.
        Каждая реплика: 'SPEAKER_XX: текст'
        Speaker labels из диаризации сохраняются как есть (SPEAKER_00, SPEAKER_01).
        """
        lines = [f'{turn["speaker"]}: {turn["text"]}' for turn in chunk]
        return "\n".join(lines)

    @staticmethod
    def _build_json_instruction(response_format: type[BaseModel]) -> str:
        """Строит инструкцию для JSON-ответа на основе Pydantic-модели."""
        schema = response_format.model_json_schema()
        return (
            "\n\nОтветь ТОЛЬКО валидным JSON объектом без markdown-разметки, "
            "соответствующим следующей JSON Schema:\n"
            f"```json\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n```"
        )

    @staticmethod
    def _parse_json_response(text: str, response_format: type[BaseModel]) -> BaseModel:
        """Извлекает JSON из текста ответа и валидирует через Pydantic."""
        content = text.strip()
        # Убираем markdown code block если есть
        if content.startswith("```"):
            # Убираем первую строку (```json) и последнюю (```)
            lines = content.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines)
        return response_format.model_validate_json(content)

    async def complete_structured(
        self,
        system_prompt: str,
        user_content: str,
        response_format: type[BaseModel],
    ) -> BaseModel:
        """Вызов LLM с structured output. Возвращает Pydantic-модель."""
        augmented_prompt = system_prompt + self._build_json_instruction(response_format)
        text = await self.complete(augmented_prompt, user_content)
        return self._parse_json_response(text, response_format)

    async def chat_structured(
        self,
        messages: list[dict],
        response_format: type[BaseModel],
    ) -> BaseModel:
        """Вызов LLM с multi-turn messages и structured output."""
        json_instruction = self._build_json_instruction(response_format)

        gigachat_messages = []
        for msg in messages:
            role = MessagesRole.SYSTEM if msg["role"] == "system" else (
                MessagesRole.ASSISTANT if msg["role"] == "assistant" else MessagesRole.USER
            )
            content = msg["content"]
            # Добавляем JSON-инструкцию к system prompt
            if role == MessagesRole.SYSTEM:
                content += json_instruction
            gigachat_messages.append(Messages(role=role, content=content))

        response = await self._client.achat(
            Chat(
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                messages=gigachat_messages,
            )
        )
        text = response.choices[0].message.content or ""
        return self._parse_json_response(text, response_format)

    async def map_reduce_structured(
        self,
        chunks: list[list[dict]],
        map_prompt: str,
        reduce_prompt: str,
        result_type: type[BaseModel],
    ) -> BaseModel:
        """
        Map-reduce с structured output на reduce-шаге.

        Map phase: plain text через complete() (промежуточные результаты).
        Reduce phase: structured output через complete_structured().
        Один чанк: сразу complete_structured() без reduce.
        """
        total = len(chunks)

        # Один чанк — сразу structured output
        if total == 1:
            formatted = self._format_chunk(chunks[0])
            return await self.complete_structured(
                map_prompt, formatted, result_type
            )

        # Map phase: plain text (промежуточные результаты)
        partial_results: list[str] = []
        running_summary = ""

        for i, chunk in enumerate(chunks, start=1):
            formatted = self._format_chunk(chunk)

            context_parts = [f"Часть {i} из {total}."]
            if running_summary:
                context_parts.append(
                    f"Краткое содержание предыдущих частей: {running_summary}"
                )
            user_content = "\n".join(context_parts) + "\n\n" + formatted

            result = await self.complete(map_prompt, user_content)
            partial_results.append(result)

            # Running summary для следующего чанка
            if i < total:
                summary_prompt = (
                    "Сформулируй краткое содержание следующего текста в 2-3 предложениях. "
                    "Сохрани ключевые темы и упомянутых спикеров."
                )
                running_summary = await self.complete(summary_prompt, result)

        # Reduce phase: structured output
        combined = "\n\n---\n\n".join(
            f"Часть {i}: {r}" for i, r in enumerate(partial_results, start=1)
        )
        return await self.complete_structured(
            reduce_prompt, combined, result_type
        )

    async def close(self) -> None:
        """Закрытие HTTP-клиента."""
        await self._client.aclose()
