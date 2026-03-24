# Project Research Summary

**Project:** Speechmate v1.1 — Web Frontend
**Domain:** React SPA для платформы анализа аудио на основе LLM
**Researched:** 2026-03-24
**Confidence:** HIGH

## Executive Summary

Speechmate v1.1 — добавление React SPA к существующей платформе из четырёх Python-микросервисов. Задача не нова по паттернам: ChatGPT-подобный интерфейс с загрузкой файлов, polling статуса и чатом — хорошо задокументированный класс продуктов. Стек выбран консервативно (React 19 + Vite + shadcn/ui + TanStack Query + Zustand) и целиком подтверждён официальными источниками. Архитектура предполагает прямые вызовы с фронтенда к двум сервисам (data_ingress:8001, llm_analysis:8003) через Vite proxy в dev и Nginx в production — API gateway не нужен для двух точек интеграции.

Ключевой риск — три отсутствующих backend endpoint, которые блокируют всю разработку фронтенда. Самый критичный: модель Recording в PostgreSQL не имеет поля `status`, без которого невозможен экран ожидания с polling. Три endpoint (GET /recordings, GET /recordings/{id}/status, GET /recordings/{id}/transcript) и CORS необходимо реализовать до начала frontend-разработки — это жёсткая зависимость, подтверждённая как в FEATURES.md, так и в ARCHITECTURE.md.

Рекомендуемый порядок: backend-дополнения сначала, затем scaffold фронтенда, затем upload + processing flow как первый вертикальный срез, и наконец полный workspace. Все 5 критических pitfall устраняются архитектурными решениями (TanStack Query, отдельные Axios instances, Vite proxy), а не отдельными задачами.

## Key Findings

### Recommended Stack

React 19 + TypeScript + Vite — базовый стек, зафиксированный в PROJECT.md. shadcn/ui с Tailwind CSS v4 обеспечивает компонентную библиотеку без npm vendor lock-in (CLI-генератор, компоненты копируются в проект). TanStack Query v5 — единственный правильный выбор для polling и server state: автоматическая очистка при unmount, кэш, devtools. Zustand v4 для UI state — минимальный footprint против Redux.

**Ключевые технологии:**
- React 19 + TypeScript: UI framework — зафиксировано в проекте
- Vite 6: build tool и dev proxy к двум FastAPI сервисам
- shadcn/ui + Tailwind v4: компоненты без npm vendor lock-in (CLI, не пакет)
- TanStack Query v5: polling, кэш, mutations — закрывает всю server state логику
- Zustand v4: UI state (selectedRecording, panelStates) — минимальный footprint
- Axios v1.7: два инстанса (ingressApi, analysisApi) с разными baseURL
- react-dropzone v14: drag & drop загрузка аудио
- React Router v6: три маршрута (/, /recordings/:id/processing, /recordings/:id)

**Предупреждения:**
- Tailwind v4 вышел в феврале 2025 — проверить совместимость shadcn/ui CLI перед `npx shadcn@latest init`
- React 19 — проверить совместимость всех библиотек; при проблемах откатиться на 18

### Expected Features

Исследование конкурентов (Otter.ai, Fireflies.ai, Fathom, tl;dv, Granola) выявило 8 table stakes и 2 дифференциатора.

**Must have (table stakes):**
- Upload Page с drag & drop, прогрессом, валидацией типа файла
- Processing Status Screen с шагами (uploaded → transcribing → diarizing → ready) и polling каждые 3 сек
- Recording History Sidebar (как список чатов в ChatGPT)
- Chat Interface (center panel, история сохраняется)
- Analysis Panel (Summary, Тезисы, Action Items, FAQ)
- Diarized Transcript Viewer (speaker labels + текст реплик)
- Error States с объяснением и retry на каждом шаге
- Responsive 3-column Layout (collapsible panels)

**Should have (дифференциаторы):**
- Markdown rendering в ответах чата и анализах
- Цитаты с attribution к конкретному спикеру

**Defer (v2+):**
- Авторизация — отложена на v1.2
- Streaming LLM ответов — backend не поддерживает SSE
- Audio playback — не core value для v1
- Search по записям — требует полнотекстовый индекс
- Export PDF/DOCX — отдельная большая задача
- Batch upload, Dark/Light theme toggle

### Architecture Approach

SPA обращается к двум сервисам напрямую через Vite proxy (dev) и Nginx (prod) — без API gateway. Структура компонентов следует маршрутам: UploadPage → ProcessingPage → WorkspacePage. Workspace — трёхколоночный layout (Sidebar | ChatPanel | RightPanel). Все data-fetching паттерны централизованы через TanStack Query с queryKey, включающим recordingId для автоматической инвалидации при переключении записей.

**Основные компоненты:**
1. UploadPage + DropZone — drag & drop, прогресс через Axios onUploadProgress
2. ProcessingPage — state machine polling с автоостановкой при status=ready
3. WorkspacePage (Sidebar + ChatPanel + RightPanel) — основная рабочая область
4. api/ layer — два Axios инстанса, чёткое разделение по сервисам
5. Shared hooks — useRecordingStatus, useAnalysis, useChat
6. Zustand store — selectedRecording, panelStates

**Backend-дополнения (блокируют фронтенд):**
- `GET /recordings` (data_ingress) — список для sidebar
- `GET /recordings/{id}/status` (data_ingress) — polling статуса
- `PATCH /internal/recordings/{id}/status` (data_ingress) — HTTP callback от воркеров
- `GET /recordings/{id}/transcript` (llm_analysis или data_ingress) — просмотр транскрипции
- Поле `status` + Alembic миграция в модели Recording

### Critical Pitfalls

1. **Отсутствие поля status в Recording** — добавить `status: str` в PostgreSQL модель, Alembic миграция, HTTP callback от transcription_service и dialogue_detection. Без этого экран ожидания невозможен.
2. **CORS не настроен на FastAPI сервисах** — добавить CORSMiddleware на data_ingress и llm_analysis_service в самом начале backend фазы, иначе браузер блокирует все запросы.
3. **Polling не останавливается при unmount** — использовать TanStack Query refetchInterval, не ручной setInterval. Query автоматически cancels при unmount.
4. **Путаница с двумя backend URL** — два отдельных Axios инстанса (ingressApi, analysisApi) + Vite proxy с разными префиксами (/api/ingress/*, /api/analysis/*).
5. **Upload без progress indicator** — аудиофайлы 50-500MB, Axios onUploadProgress callback + progress bar обязательны.

## Implications for Roadmap

Исследование однозначно указывает на 4-фазную структуру с вертикальными срезами.

### Phase 1: Backend API Extensions

**Rationale:** Три новых endpoint и отсутствующее поле status — жёсткий blocker для всего фронтенда. Пока backend не готов, ни одна frontend фича не может быть проверена end-to-end. CORS — первый шаг этой фазы.
**Delivers:** Рабочий backend API, готовый к интеграции с фронтендом
**Addresses:** Recording History Sidebar, Processing Status Screen, Transcript Viewer (из FEATURES.md)
**Avoids:** Pitfall #1 (no status field), Pitfall #2 (CORS)
**Backend tasks:**
- Добавить `status` поле в модель Recording + Alembic миграция
- `GET /recordings` — список с пагинацией для sidebar
- `GET /recordings/{id}/status` — статус для polling
- `PATCH /internal/recordings/{id}/status` — callback от воркеров
- `GET /recordings/{id}/transcript` — диаризованная транскрипция
- CORSMiddleware на data_ingress и llm_analysis_service

### Phase 2: Frontend Scaffold

**Rationale:** Базовая структура фронтенда (Vite project, routing, providers, API layer, layout shell) необходима до любой конкретной фичи. Это фундамент, на котором строится всё остальное.
**Delivers:** Navigable app skeleton — приложение открывается, маршруты работают, API layer готов
**Uses:** Vite 6, React Router v6, TanStack Query, Zustand, shadcn/ui init, два Axios инстанса
**Implements:** App, Router, Providers, api/ layer, layout shell
**Avoids:** Pitfall #4 (URL confusion), Pitfall #11 (no error boundary)

### Phase 3: Upload + Processing Flow

**Rationale:** Первый полный user journey — загрузить файл и дождаться готовности. Зависит от Phase 1 (backend status endpoint) и Phase 2 (scaffold). Это вертикальный срез: от drag & drop до перехода в workspace.
**Delivers:** Полный upload → ready flow — пользователь загружает файл, видит прогресс обработки, попадает в workspace
**Addresses:** Upload Page, Processing Status Screen, Error States (FEATURES.md)
**Uses:** react-dropzone, TanStack Query refetchInterval, Axios onUploadProgress
**Avoids:** Pitfall #3 (polling не останавливается), Pitfall #5 (нет upload progress)

### Phase 4: Workspace — Sidebar + Chat + Analysis + Transcript

**Rationale:** Основная рабочая область после готовности записи. Все три панели связаны — записи переключаются через sidebar, контент обновляется в chat и right panel. TanStack Query queryKey с recordingId обеспечивает автоматическую инвалидацию при переключении.
**Delivers:** Полный user experience — история записей, чат, анализы (Summary/Тезисы/Action Items/FAQ), просмотр транскрипции
**Addresses:** Chat Interface, Analysis Panel, Transcript Viewer, Sidebar, Responsive Layout, Markdown rendering (FEATURES.md)
**Avoids:** Pitfall #6 (layout breaks), Pitfall #7 (stale analysis data), Pitfall #8 (chat history reload), Pitfall #9 (transcript virtualization)

### Phase Ordering Rationale

- Backend-first в Phase 1: три endpoint — жёсткий blocker, без них невозможна любая end-to-end проверка
- Scaffold до фич в Phase 2: Vite proxy конфигурация и Axios инстансы нужны для Phase 3 и 4
- Upload + Processing раньше Workspace в Phase 3: это входная точка приложения, без неё некуда попасть
- Workspace последним в Phase 4: зависит от готового статуса "ready" (Phase 1+3) и scaffold (Phase 2)
- Каждая фаза — вертикальный срез: бэкенд + фронтенд вместе, не горизонтальный разрез по слоям

### Research Flags

Фазы, требующие углублённого research во время планирования:
- **Phase 1:** Механизм обновления статуса — HTTP callback от воркеров выбран как стратегия, но нужно проверить, поддерживают ли transcription_service и dialogue_detection исходящие HTTP вызовы. Альтернатива — data_ingress слушает RabbitMQ события напрямую.
- **Phase 1:** Расположение transcript endpoint — может жить в data_ingress (PostgreSQL + S3) или llm_analysis_service (MongoDB). Нужно проверить схему данных перед реализацией.
- **Phase 4:** Формат transcript — raw WhisperX сегменты или нормализованный? Влияет на компонент TranscriptViewer.

Фазы со стандартными паттернами (research-phase не нужен):
- **Phase 2:** Frontend scaffold с Vite + shadcn/ui — исчерпывающая документация, хорошо известные паттерны
- **Phase 3:** react-dropzone + TanStack Query polling — стандартные паттерны, задокументированы

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Все библиотеки подтверждены официальными источниками, версии актуальны |
| Features | HIGH | Основан на анализе 5 прямых конкурентов + ChatGPT UI patterns |
| Architecture | HIGH | Прямые вызовы к двум сервисам, стандартный Vite proxy паттерн |
| Pitfalls | HIGH | 16 pitfalls, все с конкретными предотвращениями и фазами |

**Overall confidence:** HIGH

### Gaps to Address

- **Формат recording_id:** UUID (PostgreSQL) vs MongoDB ObjectId — проверить существующий код data_ingress перед реализацией routing. Влияет на Phase 2 и 3.
- **Status callback механизм:** HTTP callback vs слушание RabbitMQ в data_ingress — нужно проверить текущий код воркеров до Phase 1.
- **Расположение transcript endpoint:** data_ingress vs llm_analysis_service — проверить схему хранения транскрипции до Phase 1.
- **Совместимость shadcn/ui CLI с Tailwind v4:** Проверить экспериментально до `npx shadcn@latest init` в Phase 2.

## Sources

### Primary (HIGH confidence)
- Официальная документация TanStack Query v5 — polling, mutations, cache invalidation
- Официальная документация Vite 6 — proxy configuration, SPA fallback
- shadcn/ui официальный сайт — CLI usage, Tailwind v4 compatibility
- Официальная документация React Router v6 — routing patterns
- Официальная документация Zustand v4 — store patterns
- Официальная документация Axios v1.7 — onUploadProgress, instances

### Secondary (MEDIUM confidence)
- Конкурентный анализ: Otter.ai, Fireflies.ai, Fathom, tl;dv, Granola — UX patterns и feature set
- react-markdown v9 — rendering LLM markdown output
- @tanstack/react-virtual — виртуализация для длинных транскрипций

### Tertiary (LOW confidence)
- Форматы хранения транскрипций в существующих сервисах — нужна проверка кода
- HTTP callback совместимость воркеров — нужна проверка существующего кода

---
*Research completed: 2026-03-24*
*Ready for roadmap: yes*
