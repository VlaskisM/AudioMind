from pydantic import BaseModel


# --- Summary ---
class SummaryResult(BaseModel):
    """Structured output для краткого содержания."""

    summary: str  # Связный текст 3-5 абзацев
    topics: list[str]  # Ключевые темы (3-7 штук)


# --- Key Points ---
class KeyPoint(BaseModel):
    """Один ключевой тезис с привязкой к спикеру."""

    point: str  # Формулировка тезиса
    speaker: str  # SPEAKER_00, SPEAKER_01, ...


class KeyPointsResult(BaseModel):
    """Structured output для ключевых тезисов."""

    key_points: list[KeyPoint]


# --- Action Items ---
class ActionItem(BaseModel):
    """Одно действие с ответственным и контекстом."""

    action: str  # Что нужно сделать
    assignee: str  # Кто ответственный (speaker label)
    context: str  # Контекст из транскрипции (1-2 предложения)


class ActionItemsResult(BaseModel):
    """Structured output для action items."""

    action_items: list[ActionItem]


# --- FAQ ---
class FaqItem(BaseModel):
    """Одна пара вопрос-ответ из FAQ."""

    question: str  # Конкретный вопрос по содержанию записи
    answer: str  # Ответ на основе транскрипции


class FaqResult(BaseModel):
    """Structured output для FAQ."""

    faq: list[FaqItem]
