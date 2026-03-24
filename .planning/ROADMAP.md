# Roadmap: Speechmate

## Milestones

- ✅ **v1.0 LLM Analysis Service** - Phases 1-4 (shipped 2026-03-22)
- 🚧 **v1.1 Web Frontend** - Phases 5-8 (in progress)

## Phases

<details>
<summary>✅ v1.0 LLM Analysis Service (Phases 1-4) - SHIPPED 2026-03-22</summary>

### Phase 1: Foundation
**Goal**: Скелет сервиса, LLM-клиент, chunking, TranscriptionReader, очистка badge_id
**Plans**: 3 plans

Plans:
- [x] 01-01: Удаление badge_id из data_ingress
- [x] 01-02: Скелет llm_analysis_service (Docker, MongoDB, FastAPI)
- [x] 01-03: MongoDB readers, speaker-boundary chunking, LLM-клиент

### Phase 2: Core Analysis
**Goal**: Summary, тезисы, action items, кэширование, API эндпоинты
**Plans**: 2 plans

Plans:
- [x] 02-01: Модели, промпты, AnalysisRepository
- [x] 02-02: AnalysisService, POST-эндпоинты анализа

### Phase 3: FAQ
**Goal**: Генерация FAQ по материалу записи
**Plans**: 1 plan

Plans:
- [x] 03-01: FAQ модели, промпты, endpoint

### Phase 4: Chat with Transcript
**Goal**: Свободный чат по записи с историей сессий
**Plans**: 2 plans

Plans:
- [x] 04-01: Chat service и data layer
- [x] 04-02: Chat web layer и интеграция

</details>

### 🚧 v1.1 Web Frontend (In Progress)

**Milestone Goal:** Веб-интерфейс в стиле ChatGPT для работы с аудиозаписями — загрузка, ожидание транскрипции, чат по записи, панель быстрых анализов, просмотр транскрипции.

- [x] **Phase 5: Backend API** - Эндпоинты статуса, списка записей и транскрипции + CORS (completed 2026-03-24)
- [x] **Phase 6: Frontend Scaffold** - React + Vite + shadcn/ui проект с routing и API layer (completed 2026-03-24)
- [ ] **Phase 7: Upload & Processing** - Загрузка аудио и экран ожидания обработки
- [ ] **Phase 8: Workspace** - Сайдбар + чат + анализы + транскрипция

## Phase Details

### Phase 5: Backend API
**Goal**: Бэкенд готов к интеграции с фронтендом — все эндпоинты для статуса, списка записей и транскрипции работают, CORS настроен
**Depends on**: Phase 4 (v1.0 complete)
**Requirements**: BAPI-01, BAPI-02, BAPI-03, BAPI-04, BAPI-05, BAPI-06
**Success Criteria** (what must be TRUE):
  1. Фронтенд-приложение с localhost может выполнять запросы к data_ingress и llm_analysis_service без CORS-ошибок
  2. Клиент получает актуальный статус записи (uploaded/transcribing/diarizing/ready/failed) через GET-запрос
  3. Клиент получает пагинированный список записей с метаданными (имя файла, дата, статус)
  4. Клиент получает диаризованную транскрипцию записи (спикер + реплики) через GET-запрос
  5. Статус записи автоматически обновляется при прохождении каждого этапа пайплайна
**Plans**: 2 plans

Plans:
- [x] 05-01: data_ingress — модель Recording (status/original_filename/error_message), Alembic миграция, эндпоинты статуса/списка/PATCH, CORS
- [ ] 05-02: llm_analysis_service — transcript endpoint + CORS, worker HTTP callbacks для обновления статуса

### Phase 6: Frontend Scaffold
**Goal**: React SPA запускается, маршруты работают, API layer подключён к двум бэкенд-сервисам через proxy
**Depends on**: Phase 5
**Requirements**: SCAF-01, SCAF-02, SCAF-03
**Success Criteria** (what must be TRUE):
  1. Приложение запускается в Docker и открывается в браузере на localhost
  2. Переход по URL `/`, `/recordings/:id/processing`, `/recordings/:id` отображает соответствующие страницы-заглушки
  3. API-вызовы с фронтенда проксируются к data_ingress и llm_analysis_service без ручной настройки URL
**Plans**: 1 plan

Plans:
- [x] 06-01: Vite + React + shadcn/ui проект, routing, API layer с proxy, Docker

### Phase 7: Upload & Processing
**Goal**: Пользователь может загрузить аудиофайл и дождаться готовности записи — первый полный user journey от входа до workspace
**Depends on**: Phase 6
**Requirements**: UPLD-01, UPLD-02, UPLD-03, UPLD-04
**Success Criteria** (what must be TRUE):
  1. Пользователь перетаскивает аудиофайл на страницу (или выбирает через file picker) и загрузка начинается
  2. Пользователь видит progress bar во время загрузки файла на сервер
  3. После загрузки пользователь видит экран ожидания с текущим шагом обработки (transcribing -> diarizing -> ready)
  4. При ошибке загрузки или обработки пользователь видит понятное сообщение с возможностью повторить
  5. После готовности записи пользователь автоматически попадает в workspace
**Plans**: 2 plans

Plans:
- [ ] 07-01: Upload page — react-dropzone, progress bar, upload API, error handling
- [ ] 07-02: Processing page — status polling, stepper UI, auto-redirect, error display

### Phase 8: Workspace
**Goal**: Пользователь работает с записью в полноценном интерфейсе — история записей, чат с цитатами, быстрые анализы, просмотр транскрипции
**Depends on**: Phase 7
**Requirements**: WRKS-01, WRKS-02, WRKS-03, WRKS-04, WRKS-05
**Success Criteria** (what must be TRUE):
  1. Пользователь видит список своих записей в sidebar и может переключаться между ними — контент обновляется
  2. Пользователь вводит вопрос по записи в чат и получает ответ с цитатой из транскрипции
  3. Пользователь нажимает кнопку анализа (summary/тезисы/action items/FAQ) и видит результат в правой панели
  4. Пользователь просматривает диаризованную транскрипцию (спикер -> реплика) в правой панели
  5. Трёхколоночный layout с возможностью сворачивания sidebar и правой панели
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD
- [ ] 08-03: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 5 -> 6 -> 7 -> 8

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | Complete | 2026-03-22 |
| 2. Core Analysis | v1.0 | 2/2 | Complete | 2026-03-22 |
| 3. FAQ | v1.0 | 1/1 | Complete | 2026-03-22 |
| 4. Chat with Transcript | v1.0 | 2/2 | Complete | 2026-03-22 |
| 5. Backend API | v1.1 | 2/2 | Complete | 2026-03-24 |
| 6. Frontend Scaffold | v1.1 | 1/1 | Complete | 2026-03-24 |
| 7. Upload & Processing | v1.1 | 0/? | Not started | - |
| 8. Workspace | v1.1 | 0/? | Not started | - |
