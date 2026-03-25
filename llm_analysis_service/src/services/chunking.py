import re

import tiktoken


# Компилируем один раз на уровне модуля
_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])(?:\s|\n)')


class ChunkingService:
    """Разбивает диаризованную транскрипцию на чанки по границам смены спикеров."""

    DEFAULT_MAX_TOKENS = 12_000

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self._enc = tiktoken.get_encoding("cl100k_base")
        self._max_tokens = max_tokens
        # Кэш токенов speaker prefixes — в записи обычно 2-5 спикеров
        self._prefix_cache: dict[str, int] = {}

    def _prefix_tokens(self, speaker: str) -> int:
        """Токены speaker prefix с кэшированием."""
        cached = self._prefix_cache.get(speaker)
        if cached is not None:
            return cached
        tokens = len(self._enc.encode(f"{speaker}: "))
        self._prefix_cache[speaker] = tokens
        return tokens

    def _text_tokens(self, text: str) -> int:
        return len(self._enc.encode(text))

    def _turn_tokens(self, turn: dict) -> int:
        return self._prefix_tokens(turn["speaker"]) + self._text_tokens(turn["text"])

    def chunk_by_speakers(self, speakers: list[dict]) -> list[list[dict]]:
        """
        Принимает speakers из diarization document.
        Возвращает список чанков, каждый чанк -- список turn dict.

        Алгоритм:
        1. Flatten + sort по start time (диаризация хранит по спикерам, не хронологически)
        2. Группировка в чанки с границами на смене спикера
        3. Fallback: длинный монолог одного спикера разрезается на границе предложений
        """
        # Flatten + sort за один проход
        turns = sorted(
            (
                {"speaker": sp["label"], "text": seg["text"], "start": seg["start"], "end": seg["end"]}
                for sp in speakers
                for seg in sp.get("segments", ())
            ),
            key=lambda t: t["start"],
        )

        if not turns:
            return []

        max_tokens = self._max_tokens
        chunks: list[list[dict]] = []
        current_chunk: list[dict] = []
        current_tokens = 0

        for turn in turns:
            t_tokens = self._turn_tokens(turn)

            # Один turn превышает лимит — разрезаем монолог
            if t_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_tokens = 0

                for sub_turn in self._split_long_monologue(turn):
                    sub_tokens = self._turn_tokens(sub_turn)
                    if current_tokens + sub_tokens > max_tokens and current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = []
                        current_tokens = 0
                    current_chunk.append(sub_turn)
                    current_tokens += sub_tokens
                continue

            # Проверяем лимит чанка
            if current_tokens + t_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [turn]
                current_tokens = t_tokens
            else:
                current_chunk.append(turn)
                current_tokens += t_tokens

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_long_monologue(self, turn: dict) -> list[dict]:
        """
        Fallback: разрезает длинный монолог на границе предложений.
        Сохраняет speaker label в каждом фрагменте.
        Каждый фрагмент <= max_tokens.
        """
        sentences = _SENTENCE_SPLIT.split(turn["text"])
        sentences = [s for s in (s.strip() for s in sentences) if s]

        budget = self._max_tokens - self._prefix_tokens(turn["speaker"])
        sentence_tokens = [self._text_tokens(s) for s in sentences]

        speaker = turn["speaker"]
        start = turn["start"]
        end = turn["end"]

        fragments: list[dict] = []
        current_sentences: list[str] = []
        current_tokens = 0

        for sentence, s_tokens in zip(sentences, sentence_tokens):
            separator_cost = 1 if current_sentences else 0

            if current_tokens + separator_cost + s_tokens > budget and current_sentences:
                fragments.append({
                    "speaker": speaker,
                    "text": " ".join(current_sentences),
                    "start": start,
                    "end": end,
                })
                current_sentences = [sentence]
                current_tokens = s_tokens
            else:
                current_sentences.append(sentence)
                current_tokens += separator_cost + s_tokens

        if current_sentences:
            fragments.append({
                "speaker": speaker,
                "text": " ".join(current_sentences),
                "start": start,
                "end": end,
            })

        return fragments
