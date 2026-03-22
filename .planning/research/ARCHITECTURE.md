# Architecture Research: LLM Analysis Service

**Domain:** LLM analysis microservice integration
**Date:** 2026-03-22
**Context:** 4th service in existing event-driven platform (data_ingress → transcription → diarization → **analysis**)

## Component Overview

```
┌─────────────────────────────────────────────────┐
│                LLM Analysis Service              │
│                                                  │
│  ┌──────────┐   ┌────────────────┐              │
│  │ HTTP API │──▶│ AnalysisService│──┐           │
│  │ (FastAPI)│   └────────────────┘  │           │
│  │          │   ┌────────────────┐  │           │
│  │          │──▶│  ChatService   │──┤           │
│  └──────────┘   └────────────────┘  │           │
│                                      ▼           │
│                 ┌────────────────┐ ┌──────────┐ │
│                 │ PromptManager  │ │ LLMClient│ │
│                 │ (Jinja2)       │ │ (OpenAI) │ │
│                 └────────────────┘ └──────────┘ │
│                                      │           │
│  ┌──────────────────┐  ┌───────────────────┐   │
│  │TranscriptionReader│  │AnalysisRepository │   │
│  │(reads from Mongo) │  │ChatRepository     │   │
│  └──────────────────┘  │(writes to Mongo)   │   │
│                         └───────────────────┘   │
└──────────────────────┬──────────────────────────┘
                       │
              ┌────────┴────────┐
              │    MongoDB      │
              │ - transcriptions│
              │ - diarizations  │
              │ - analyses      │
              │ - chat_sessions │
              └─────────────────┘
```

## Components

### 1. HTTP API (FastAPI)
- **Граница:** Принимает HTTP запросы, валидирует, возвращает JSON
- **Эндпоинты:**
  - `POST /recordings/{id}/analyze` — запуск анализа (type: summary|key_points|action_items|faq)
  - `GET /recordings/{id}/analyses` — получить сохранённые результаты
  - `POST /recordings/{id}/chat` — отправить сообщение в чат
  - `GET /recordings/{id}/chat/history` — история чата
- **Зависимости:** AnalysisService, ChatService

### 2. AnalysisService
- **Граница:** Оркестрация анализа — проверка кэша, загрузка транскрипции, вызов LLM, сохранение
- **Логика:**
  1. Проверить кэш (recording_id + analysis_type)
  2. Если нет → загрузить транскрипцию + диаризацию из MongoDB
  3. Подготовить промпт через PromptManager
  4. Вызвать LLMClient
  5. Сохранить результат через AnalysisRepository
- **Зависимости:** TranscriptionReader, PromptManager, LLMClient, AnalysisRepository

### 3. ChatService
- **Граница:** Управление чат-сессиями — история, контекст, вызов LLM
- **Логика:**
  1. Загрузить/создать сессию
  2. Собрать контекст: транскрипция + история сообщений
  3. Вызвать LLMClient с system prompt + context + user message
  4. Сохранить пару (вопрос, ответ) в историю
- **Управление контекстом:** Обрезка старых сообщений при приближении к лимиту токенов
- **Зависимости:** TranscriptionReader, LLMClient, ChatRepository

### 4. PromptManager
- **Граница:** Загрузка и рендеринг Jinja2 шаблонов промптов
- **Промпты:** `summary.j2`, `key_points.j2`, `action_items.j2`, `faq.j2`, `chat_system.j2`
- **Переменные:** transcription_text, speakers, duration, language, analysis_type

### 5. LLMClient
- **Граница:** Обёртка над OpenAI AsyncClient
- **Ответственность:** Вызов API, structured output (response_format), retry, подсчёт токенов
- **Конфигурация:** model, temperature, max_tokens через env vars

### 6. TranscriptionReader
- **Граница:** Чтение транскрипции + диаризации из MongoDB, форматирование для промпта
- **Формат вывода:** Текст с метками спикеров и таймкодами
- **Chunking:** Разбивка длинных транскрипций по сегментам спикеров

### 7. AnalysisRepository / ChatRepository
- **Граница:** CRUD для результатов анализа и чат-сессий в MongoDB
- **Коллекции:** `analyses`, `chat_sessions`

## Data Flow

### Анализ (summary / key_points / action_items / faq)

```
Client → POST /recordings/{id}/analyze?type=summary
  → AnalysisService.analyze(recording_id, type)
    → Check cache (AnalysisRepository.find)
    → If cached → return cached result
    → TranscriptionReader.get(recording_id) → formatted text
    → PromptManager.render("summary", {text, speakers})
    → LLMClient.complete(prompt) → structured response
    → AnalysisRepository.save(recording_id, type, result)
    → return result
```

### Чат

```
Client → POST /recordings/{id}/chat {message: "..."}
  → ChatService.send(recording_id, message)
    → TranscriptionReader.get(recording_id) → context
    → ChatRepository.get_history(recording_id, session_id)
    → PromptManager.render("chat_system", {context})
    → LLMClient.chat([system, ...history, user_message])
    → ChatRepository.save_message(session_id, user_msg, assistant_msg)
    → return response
```

## Стратегия кэширования

**Ключ кэша:** `(recording_id, analysis_type, prompt_version)`
- Тот же recording_id + тот же тип → вернуть кэш
- Регенерация → удалить кэш, вызвать LLM заново
- Смена prompt_version → кэш невалиден

## Обработка длинных транскрипций

**Стратегия: Map-Reduce**
1. Подсчитать токены через tiktoken
2. Если < лимита модели → отправить целиком
3. Если > лимита → разбить на чанки по сегментам спикеров
4. Map: получить промежуточный результат для каждого чанка
5. Reduce: объединить промежуточные результаты в финальный

**Для чата:** Транскрипция обрезается до релевантных секций (можно использовать простой поиск по ключевым словам).

## Порядок сборки

| Фаза | Компоненты | Зависимости |
|------|-----------|-------------|
| 1 | Скелет сервиса, конфигурация, Docker | Существующая инфраструктура |
| 2 | TranscriptionReader, LLMClient, PromptManager | Фаза 1 |
| 3 | AnalysisService + эндпоинты (summary, key_points, action_items, faq) | Фаза 2 |
| 4 | Кэширование + регенерация | Фаза 3 |
| 5 | ChatService + чат эндпоинты | Фаза 2, 4 |

## Интеграция с существующей архитектурой

**Переиспользуется:**
- Docker-compose (добавляем новый сервис)
- MongoDB (новые коллекции в той же БД)
- Паттерн Repository (из transcription_service)
- Pydantic-settings конфигурация
- Структура проекта

**Новое:**
- OpenAI API интеграция
- Prompt templates
- Chat session management
- Token counting / chunking

---
*Architecture designed for consistency with existing Speechmate services*
