# Stack Research: LLM Analysis Service

**Domain:** LLM-powered transcription analysis
**Date:** 2026-03-22
**Context:** Adding LLM analysis service to existing Speechmate platform (Python async, FastAPI, MongoDB, RabbitMQ)

## Core LLM Integration

| Library | Version | Purpose | Confidence |
|---------|---------|---------|------------|
| `openai` | ^1.x | OpenAI Python SDK — async client, structured outputs, chat completions | High |
| `tiktoken` | ^0.7 | Token counting для OpenAI моделей — контроль лимитов, chunking | High |
| `pydantic` | ^2.x | Structured output validation, response schemas | High (уже в проекте) |

### OpenAI SDK

**Почему openai ^1.x:**
- Нативный async client (`AsyncOpenAI`) — совместим с текущим asyncio стеком
- `response_format` с JSON mode — гарантированный структурированный вывод
- Structured Outputs с Pydantic моделями — type-safe ответы
- Встроенный retry с exponential backoff
- Streaming поддержка для чата

**Модели:**
- `gpt-4o-mini` — основная модель для summary, тезисов, action items, FAQ (баланс цена/качество)
- `gpt-4o` — для сложных задач (чат, длинные транскрипции) если нужна точность

### Что НЕ использовать

| Library | Причина |
|---------|---------|
| `langchain` | Избыточная абстракция для нашего случая — прямой OpenAI SDK проще и прозрачнее |
| `llama-index` | Ориентирован на RAG с векторными БД — не нужен для анализа отдельных транскрипций |
| `semantic-kernel` | Microsoft-экосистема, лишняя зависимость |
| Собственные обёртки над HTTP | OpenAI SDK уже всё делает — retry, streaming, typing |

## Prompt Management

| Library | Version | Purpose | Confidence |
|---------|---------|---------|------------|
| `jinja2` | ^3.x | Шаблонизация промптов с переменными | High |

**Подход:** Промпты как Jinja2 шаблоны в отдельной директории (`src/prompts/`). Версионирование через имена файлов или git.

**Почему не:**
- Специализированные prompt frameworks (promptflow, guidance) — оверинжиниринг для 4-5 типов промптов
- Хардкод в коде — промпты итерируются в 10-100x быстрее кода

## Web Framework & Infrastructure

| Library | Version | Purpose | Confidence |
|---------|---------|---------|------------|
| `fastapi` | ^0.110 | HTTP API — совместимо с существующим data_ingress | High (уже в проекте) |
| `motor` | ^3.x | Async MongoDB driver | High (уже в проекте) |
| `pydantic-settings` | ^2.x | Конфигурация через env vars | High (уже в проекте) |

## Переиспользование из существующих сервисов

Из текущей кодовой базы переиспользуются паттерны:
- MongoDB repository pattern (из transcription_service)
- Pydantic-settings конфигурация
- Docker-compose интеграция
- Структура проекта (src/services, src/repositories, src/db)

## Новые зависимости (только для LLM-сервиса)

```
openai>=1.0
tiktoken>=0.7
jinja2>=3.0
```

Всё остальное уже есть в экосистеме проекта.

---
*Confidence levels: High = proven in production, Medium = good evidence, Low = experimental*
