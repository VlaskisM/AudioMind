# Project Research Summary

**Project:** Speechmate — LLM Analysis Service
**Domain:** LLM-powered audio transcription analysis microservice
**Researched:** 2026-03-22
**Confidence:** HIGH

## Executive Summary

Speechmate уже имеет рабочий event-driven пайплайн (data_ingress → transcription → diarization). Следующий шаг — четвёртый сервис: LLM analysis. Это хорошо изученная задача: берём готовые транскрипции с диаризацией из MongoDB, гоним через OpenAI GPT-4o-mini с Jinja2-шаблонами промптов, сохраняем структурированный результат обратно в MongoDB. Архитектура полностью аналогична transcription_service — те же паттерны Repository, та же Pydantic-settings конфигурация, тот же Docker-compose. Новых инфраструктурных решений минимум.

Главная техническая сложность — правильная обработка длинных транскрипций (map-reduce chunking) и контроль стоимости API. Оба вопроса имеют проверенные решения: tiktoken для подсчёта токенов, MongoDB-кэш с ключом (recording_id, type, prompt_version), gpt-4o-mini как основная модель (10-20x дешевле gpt-4o). Эти механизмы нужно закладывать с первой фазы, не откладывать.

Набор фич хорошо определён конкурентным анализом (Otter.ai, Fireflies.ai, Fathom, tl;dv). Table stakes — Summary, Key Points, Action Items, кэширование. Дифференциаторы — FAQ-генерация и Chat with Transcript. Порядок реализации диктуется зависимостями: инфраструктура → аналитические эндпоинты → чат. Авто-анализ после транскрипции, SSE streaming и fine-tuning — явные anti-features для v1.

## Key Findings

### Recommended Stack

Стек минималистичен и согласован с существующим проектом. Три новые зависимости: `openai>=1.0` (async клиент с встроенным retry), `tiktoken>=0.7` (точный подсчёт токенов для chunking), `jinja2>=3.0` (шаблонизация промптов). Всё остальное — FastAPI, motor, pydantic, pydantic-settings — уже в проекте. LangChain, llama-index и аналогичные фреймворки явно исключены: избыточная абстракция для 4-5 типовых задач.

**Core technologies:**
- `openai ^1.x`: async LLM API — нативный AsyncOpenAI, structured outputs, встроенный retry/backoff
- `tiktoken ^0.7`: подсчёт токенов — необходим для chunking решения и контроля лимитов
- `jinja2 ^3.x`: шаблоны промптов — быстрая итерация без деплоя кода
- `gpt-4o-mini`: основная модель — баланс цена/качество для summary, key points, action items, FAQ
- `gpt-4o`: fallback для сложных задач (чат, длинные транскрипции) при необходимости точности

### Expected Features

Конкурентный анализ дал чёткое разделение на волны. Must-have определяет базовую конкурентоспособность; дифференциаторы выделяют продукт; anti-features защищают от scope creep.

**Must have (table stakes):**
- Summary — ожидается всеми пользователями платформ транскрипции
- Key Points — bullet-point тезисы, базовый UX
- Action Items — извлечение обязательств с атрибуцией по спикерам
- Кэширование результатов — без него повторные запросы сжигают бюджет
- Обработка длинных транскрипций (60-120+ мин) — критично для реальных записей

**Should have (competitive):**
- FAQ-генерация — редкость у конкурентов, высокая ценность для лекций/вебинаров
- Chat with Transcript — свободный диалог по записи с сохранением истории
- Speaker Attribution — результаты привязаны к конкретным спикерам
- Регенерация — кнопка "сгенерировать заново"

**Defer (v2+):**
- Auto-analysis после транскрипции — сжигает токены на непросмотренные записи
- SSE/WebSocket streaming — усложняет архитектуру без MVP-ценности
- Cross-recording comparison — требует RAG инфраструктуру
- Export PDF/DOCX — задача фронтенда

### Architecture Approach

Сервис строится как самостоятельный FastAPI-микросервис, читающий транскрипции из общей MongoDB и записывающий результаты в новые коллекции (`analyses`, `chat_sessions`). Никакого RabbitMQ — анализ запускается явным HTTP-запросом пользователя (on-demand, не event-driven). Паттерн Repository из transcription_service переиспользуется напрямую. UoW не нужен — каждый анализ это одна атомарная запись.

**Major components:**
1. HTTP API (FastAPI) — 4 эндпоинта: analyze, get analyses, chat, chat history
2. AnalysisService — оркестрация: кэш → загрузка транскрипции → промпт → LLM → сохранение
3. ChatService — управление чат-сессиями: контекст, история, обрезка по токенам
4. PromptManager (Jinja2) — загрузка и рендеринг шаблонов из `src/prompts/`
5. LLMClient — обёртка AsyncOpenAI: structured output, retry, подсчёт токенов
6. TranscriptionReader — чтение из MongoDB, форматирование с метками спикеров и таймкодами
7. AnalysisRepository / ChatRepository — CRUD для `analyses` и `chat_sessions`

### Critical Pitfalls

1. **Naive full-transcript sends без chunking** — "lost in the middle" эффект: модель пропускает середину длинных записей. Предотвращение: map-reduce для транскрипций > 8K токенов, chunking по сегментам спикеров, tiktoken для точного подсчёта. Закладывать в Phase 1.

2. **Отсутствие кэширования** — 3-10x перерасход токенов на повторные запросы. Предотвращение: MongoDB-кэш по ключу (recording_id, type, prompt_version), инвалидация при смене промпта. Реализовать вместе с первыми анализами.

3. **Неконтролируемые расходы на API** — нет лимитов → неожиданный рост счёта. Предотвращение: rate limiting по user_id, логирование usage на каждый запрос, gpt-4o-mini по умолчанию.

4. **Галлюцинации в summary и action items** — модель "додумывает" несуществующие факты. Предотвращение: system prompt "only extract explicitly stated", temperature 0.1-0.3, требование цитаты для action items.

5. **Chat context grows unbounded** — стоимость растёт линейно с историей. Предотвращение: ограничение истории (последние N сообщений), сжатие старых в summary, обрезка транскрипции до релевантных секций.

## Implications for Roadmap

На основе исследований рекомендуется 5-фазная структура, где каждая фаза разблокирует следующую.

### Phase 1: Foundation (Service Skeleton + Infrastructure)

**Rationale:** Все компоненты верхнего уровня зависят от инфраструктуры. Chunking, async client и PromptManager нужно закладывать здесь — их сложно добавить ретроспективно.
**Delivers:** Рабочий Docker-сервис, конфигурация, LLMClient с async/retry/structured-output, TranscriptionReader с форматированием спикеров, PromptManager, базовые эндпоинты (health check).
**Addresses:** Обработка длинных транскрипций, speaker attribution в промптах.
**Avoids:** Pitfall 1 (chunking), Pitfall 3 (rate limiting + usage logging), Pitfall 6 (async client), Pitfall 7 (PromptManager), Pitfall 8 (structured output), Pitfall 9 (дизаризация в промптах).

### Phase 2: Core Analysis (Summary + Key Points + Action Items)

**Rationale:** Три table-stakes фичи имеют одинаковую архитектуру — один AnalysisService, один flow. Реализуются вместе для переиспользования кода. Кэш включается здесь же — он нужен с первого production запроса.
**Delivers:** Рабочие эндпоинты `POST /recordings/{id}/analyze` (type=summary|key_points|action_items), `GET /recordings/{id}/analyses`, MongoDB-кэш.
**Uses:** openai, tiktoken, jinja2, AnalysisRepository.
**Implements:** AnalysisService, кэширование, 3 Jinja2-шаблона промптов.
**Avoids:** Pitfall 2 (кэш), Pitfall 3 (контроль расходов).

### Phase 3: FAQ + Regeneration

**Rationale:** FAQ переиспользует AnalysisService без изменений — только новый шаблон промпта. Регенерация — инвалидация кэша. Обе задачи малы и логично группируются.
**Delivers:** FAQ-анализ, кнопка регенерации (DELETE кэша + повторный вызов).
**Implements:** `faq.j2` шаблон, логика инвалидации кэша.

### Phase 4: Chat with Transcript

**Rationale:** Зависит от TranscriptionReader (Phase 1) и всей инфраструктуры кэширования (Phase 2). Самый сложный компонент — отдельная фаза для изоляции сложности.
**Delivers:** Эндпоинты `POST /recordings/{id}/chat` и `GET /recordings/{id}/chat/history`, ChatService с управлением контекстом и историей, ChatRepository.
**Avoids:** Pitfall 5 (unbounded context growth).

### Phase 5: Hardening

**Rationale:** Graceful degradation, language detection, WhisperX error handling — полезные улучшения, но не блокируют запуск.
**Delivers:** Health check с OpenAI статусом, fallback на кэш при недоступности API, language-aware промпты, error messaging.
**Avoids:** Pitfall 10 (ошибки WhisperX), Pitfall 11 (graceful degradation), Pitfall 12 (язык промпта).

### Phase Ordering Rationale

- Инфраструктура первой — chunking и async client невозможно добавить без рефакторинга. Это единственный нарушитель порядка если отложить.
- Кэш вместе с первыми анализами — после первого production запроса повторные вызовы уже должны быть бесплатными.
- Chat последним — зависит от всех предыдущих компонентов и вносит уникальную сложность (session management, unbounded context).
- Hardening в конце — не блокирует core functionality, но повышает reliability.

### Research Flags

Фазы, которые могут потребовать `/gsd:research-phase` при планировании:
- **Phase 1 (Chunking):** Конкретная реализация map-reduce для русскоязычных транскрипций требует тестирования с реальными данными.
- **Phase 4 (Chat):** Управление контекстом при длинных транскрипциях + история — нетривиально. Стратегия обрезки транскрипции нуждается в валидации.

Фазы со стандартными паттернами (research-phase не нужен):
- **Phase 2 (Core Analysis):** Хорошо задокументированный паттерн OpenAI structured outputs + Repository.
- **Phase 3 (FAQ + Regeneration):** Прямое расширение Phase 2, минимальная новизна.
- **Phase 5 (Hardening):** Стандартные паттерны reliability инженерии.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Все технологии уже в проекте или имеют стабильные версии с официальной документацией |
| Features | HIGH | Конкурентный анализ 6 платформ + устоявшийся рынок |
| Architecture | HIGH | Прямое расширение существующей архитектуры, проверенные паттерны |
| Pitfalls | HIGH | 12 pitfalls с конкретными prevention стратегиями, большинство из production опыта |

**Overall confidence:** HIGH

### Gaps to Address

- **Оптимальный размер чанка для map-reduce:** 8K токенов как граница — эмпирическое правило, нужно валидировать на реальных транскрипциях Speechmate. Корректировать в Phase 1.
- **Rate limiting стратегия:** Исследование не определило конкретные лимиты (X запросов/час). Нужно решить на этапе планирования Phase 2 исходя из бизнес-требований.
- **Стратегия обрезки транскрипции для чата:** Простой keyword search рекомендован в ARCHITECTURE.md, но эффективность не верифицирована. Решать в Phase 4.
- **Версионирование промптов:** Механизм инвалидации кэша при смене prompt_version не специфицирован. Определить в Phase 1 (PromptManager).

## Sources

### Primary (HIGH confidence)
- Существующая кодовая база Speechmate — паттерны Repository, Docker-compose, Pydantic-settings
- OpenAI Python SDK официальная документация — AsyncOpenAI, structured outputs, response_format
- OpenAI Cookbook — "lost in the middle" эффект, chunking стратегии

### Secondary (MEDIUM confidence)
- Конкурентный анализ: Otter.ai, Fireflies.ai, Fathom, tl;dv, Granola, Recall.ai — feature research
- tiktoken документация — токен-эффективность для GPT моделей

### Tertiary (LOW confidence)
- Эмпирические оценки токенов транскрипции (15 мин ≈ 4K токенов) — нужна валидация на реальных данных Speechmate
- Граница 8K токенов для chunking — рекомендация требует A/B тестирования

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
