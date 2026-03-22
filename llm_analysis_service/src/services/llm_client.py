from openai import AsyncOpenAI


class LLMClient:
    """Обёртка над AsyncOpenAI с поддержкой map-reduce для длинных транскрипций."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    async def complete(self, system_prompt: str, user_content: str) -> str:
        """Один вызов LLM. Возвращает текстовый ответ."""
        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
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

    async def close(self) -> None:
        """Закрытие HTTP-клиента."""
        await self._client.close()
