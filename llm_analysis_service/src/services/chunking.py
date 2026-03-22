import re

import tiktoken


class ChunkingService:
    """Разбивает диаризованную транскрипцию на чанки по границам смены спикеров."""

    DEFAULT_MAX_TOKENS = 12_000

    def __init__(self, model: str = "gpt-4o-mini", max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self._enc = tiktoken.encoding_for_model(model)
        self._max_tokens = max_tokens

    def chunk_by_speakers(self, speakers: list[dict]) -> list[list[dict]]:
        """
        Принимает speakers из diarization document.
        Возвращает список чанков, каждый чанк -- список turn dict.

        Алгоритм:
        1. Flatten: все сегменты всех спикеров в flat list of turns
        2. Sort по start time (диаризация хранит по спикерам, не хронологически)
        3. Группировка в чанки с границами на смене спикера
        4. Fallback: длинный монолог одного спикера разрезается на границе предложений
        """
        # Шаг 1: Flatten -- собираем все сегменты всех спикеров в единый список
        turns: list[dict] = []
        for speaker in speakers:
            label = speaker["label"]
            for segment in speaker.get("segments", []):
                turns.append({
                    "speaker": label,
                    "text": segment["text"],
                    "start": segment["start"],
                    "end": segment["end"],
                })

        # Шаг 2: Сортировка по времени начала
        turns.sort(key=lambda t: t["start"])

        if not turns:
            return []

        # Шаг 3: Группировка в чанки по границам смены спикера
        chunks: list[list[dict]] = []
        current_chunk: list[dict] = []
        current_tokens = 0

        for turn in turns:
            turn_tokens = self._count_tokens(self._format_turn(turn))

            # Если один turn превышает лимит -- разрезаем монолог
            if turn_tokens > self._max_tokens:
                # Сначала сохраняем текущий чанк, если он не пуст
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0

                # Разбиваем длинный монолог на фрагменты
                split_turns = self._split_long_monologue(turn)
                for sub_turn in split_turns:
                    sub_tokens = self._count_tokens(self._format_turn(sub_turn))
                    if current_tokens + sub_tokens > self._max_tokens and current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = []
                        current_tokens = 0
                    current_chunk.append(sub_turn)
                    current_tokens += sub_tokens
                continue

            # Проверяем, не превысит ли добавление turn лимит
            if current_tokens + turn_tokens > self._max_tokens:
                # Граница чанка -- начинаем новый
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [turn]
                current_tokens = turn_tokens
            else:
                current_chunk.append(turn)
                current_tokens += turn_tokens

        # Добавляем последний чанк
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _count_tokens(self, text: str) -> int:
        """Подсчёт токенов через tiktoken."""
        return len(self._enc.encode(text))

    def _format_turn(self, turn: dict) -> str:
        """Форматирует turn для подсчёта токенов: 'SPEAKER_XX: text'"""
        return f'{turn["speaker"]}: {turn["text"]}'

    def _split_long_monologue(self, turn: dict) -> list[dict]:
        """
        Fallback: разрезает длинный монолог на границе предложений.
        Сохраняет speaker label в каждом фрагменте.
        Разделители: '. ', '! ', '? ', '.\\n'
        Каждый фрагмент <= max_tokens.
        """
        # Разбиваем текст на предложения по границам
        sentences = re.split(r'(?<=[.!?])(?:\s|\n)', turn["text"])
        sentences = [s.strip() for s in sentences if s.strip()]

        fragments: list[dict] = []
        current_text = ""
        current_tokens = 0

        for sentence in sentences:
            # Считаем токены для форматированного текста с speaker label
            candidate = f"{current_text} {sentence}".strip() if current_text else sentence
            candidate_tokens = self._count_tokens(f'{turn["speaker"]}: {candidate}')

            if candidate_tokens > self._max_tokens and current_text:
                # Сохраняем текущий фрагмент
                fragments.append({
                    "speaker": turn["speaker"],
                    "text": current_text,
                    "start": turn["start"],
                    "end": turn["end"],
                })
                current_text = sentence
                current_tokens = self._count_tokens(f'{turn["speaker"]}: {sentence}')
            else:
                current_text = candidate
                current_tokens = candidate_tokens

        # Добавляем последний фрагмент
        if current_text:
            fragments.append({
                "speaker": turn["speaker"],
                "text": current_text,
                "start": turn["start"],
                "end": turn["end"],
            })

        return fragments
