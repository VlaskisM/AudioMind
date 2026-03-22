# Roadmap: Speechmate v1.0 — LLM Analysis Service

## Overview

Четвёртый микросервис в пайплайне Speechmate: LLM-анализ транскрипций. От скелета сервиса с инфраструктурой chunking/prompts до полноценного анализа (summary, тезисы, action items), затем FAQ, и наконец свободный чат по записи. Каждая фаза разблокирует следующую и доставляет завершённую пользовательскую возможность.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - Скелет сервиса, LLM-клиент, chunking, TranscriptionReader, очистка badge_id (completed 2026-03-22)
- [x] **Phase 2: Core Analysis** - Summary, тезисы, action items, кэширование, API эндпоинты (completed 2026-03-22)
- [ ] **Phase 3: FAQ** - Генерация FAQ по материалу записи
- [ ] **Phase 4: Chat with Transcript** - Свободный чат по записи с историей сессий

## Phase Details

### Phase 1: Foundation
**Goal**: Сервис запускается в Docker, умеет читать транскрипции из MongoDB с диаризацией, отправлять запросы в OpenAI с chunking для длинных записей, и badge_id удалён из data_ingress
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, INFR-04, CLEAN-01
**Success Criteria** (what must be TRUE):
  1. Сервис запускается через docker-compose и отвечает на health check
  2. Транскрипция длиннее 60 минут корректно разбивается на чанки и обрабатывается без потери контекста
  3. Результаты анализа содержат привязку к конкретным спикерам из диаризации
  4. badge_id полностью удалён из модели Recording и всех связанных эндпоинтов data_ingress
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Удаление badge_id из data_ingress (модель, schemas, routes, services, repositories, Alembic-миграция)
- [ ] 01-02-PLAN.md — Скелет llm_analysis_service (FastAPI + Docker + конфиги OpenAI/MongoDB + health check)
- [ ] 01-03-PLAN.md — MongoDB readers, speaker-boundary chunking, LLM-клиент с map-reduce

### Phase 2: Core Analysis
**Goal**: Пользователь получает структурированный анализ записи (summary, тезисы, action items) через API с кэшированием результатов
**Depends on**: Phase 1
**Requirements**: ANLZ-01, ANLZ-02, ANLZ-03, ANLZ-05, INFR-03
**Success Criteria** (what must be TRUE):
  1. Пользователь получает краткое содержание записи через POST-запрос к API
  2. Пользователь получает список ключевых тезисов через POST-запрос к API
  3. Пользователь получает action items с указанием ответственных спикеров через POST-запрос к API
  4. Повторный запрос того же анализа возвращает кэшированный результат из MongoDB без вызова LLM
  5. Каждый тип анализа доступен через отдельный API эндпоинт
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — Pydantic-модели structured outputs, промпты, LLMClient extension, AnalysisRepository для кэширования
- [ ] 02-02-PLAN.md — AnalysisService, FastAPI lifespan, POST-эндпоинты анализа, wiring

### Phase 3: FAQ
**Goal**: Пользователь получает автоматически сгенерированный FAQ по материалу записи
**Depends on**: Phase 2
**Requirements**: ANLZ-04
**Success Criteria** (what must be TRUE):
  1. Пользователь получает FAQ (вопрос-ответ пары) по содержанию записи через API
  2. FAQ-результат кэшируется и повторный запрос не вызывает LLM
**Plans**: 1 plan

Plans:
- [ ] 03-01-PLAN.md — FaqItem/FaqResult модели, промпты FAQ map/reduce, get_faq() в AnalysisService, FaqResponse schema, POST endpoint

### Phase 4: Chat with Transcript
**Goal**: Пользователь ведёт свободный диалог с LLM по контексту записи, получает ответы с цитатами, история сохраняется
**Depends on**: Phase 2
**Requirements**: CHAT-01, CHAT-02
**Success Criteria** (what must be TRUE):
  1. Пользователь задаёт вопрос по записи и получает ответ с цитатой из транскрипции
  2. История чат-сессии сохраняется в MongoDB и доступна при следующем обращении
  3. Чат корректно работает с длинными транскрипциями (контекст не превышает лимит модели)
**Plans**: TBD

Plans:
- [ ] 04-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete   | 2026-03-22 |
| 2. Core Analysis | 2/2 | Complete | 2026-03-22 |
| 3. FAQ | 0/0 | Not started | - |
| 4. Chat with Transcript | 0/0 | Not started | - |
