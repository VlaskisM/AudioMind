# Requirements: Speechmate

**Defined:** 2026-03-22, updated 2026-03-24
**Core Value:** Пользователь загружает аудио и получает структурированный анализ содержания через LLM

## v1.0 Requirements (Complete)

### Очистка (CLEAN)

- [x] **CLEAN-01**: badge_id удалён из модели Recording и всей цепочки data_ingress

### Инфраструктура (INFR)

- [x] **INFR-01**: LLM analysis service запускается как отдельный FastAPI-микросервис в Docker
- [x] **INFR-02**: Сервис корректно обрабатывает транскрипции длиннее 60 минут (chunking)
- [x] **INFR-03**: Повторный запрос анализа возвращает кэшированный результат из MongoDB
- [x] **INFR-04**: Результаты анализа привязаны к конкретным спикерам из диаризации

### Анализ (ANLZ)

- [x] **ANLZ-01**: Пользователь получает краткое содержание (summary) записи
- [x] **ANLZ-02**: Пользователь получает список ключевых тезисов
- [x] **ANLZ-03**: Пользователь получает action items с указанием ответственных
- [x] **ANLZ-04**: Пользователь получает FAQ по материалу записи
- [x] **ANLZ-05**: Каждый тип анализа доступен через отдельный API эндпоинт

### Чат (CHAT)

- [x] **CHAT-01**: Пользователь может задать вопрос по записи и получить ответ с цитатой
- [x] **CHAT-02**: История чат-сессии сохраняется в MongoDB

## v1.1 Requirements

Requirements for milestone v1.1 — Web Frontend.

### Backend API (BAPI)

- [x] **BAPI-01**: Поле `status` добавлено в модель Recording с Alembic миграцией
- [x] **BAPI-02**: CORSMiddleware настроен на data_ingress и llm_analysis_service
- [x] **BAPI-03**: `GET /recordings/{id}/status` возвращает текущий статус записи
- [x] **BAPI-04**: `GET /recordings` возвращает список записей с пагинацией
- [x] **BAPI-05**: `GET /recordings/{id}/transcript` возвращает диаризованную транскрипцию
- [x] **BAPI-06**: Статус записи обновляется при каждом событии пайплайна (uploaded → transcribing → diarizing → ready/failed)

### Upload (UPLD)

- [ ] **UPLD-01**: Пользователь загружает аудиофайл через drag & drop или file picker
- [ ] **UPLD-02**: Пользователь видит прогресс загрузки файла (progress bar)
- [ ] **UPLD-03**: Пользователь видит экран ожидания с шагами обработки (transcribing → diarizing → ready)
- [ ] **UPLD-04**: Пользователь видит информативную ошибку при сбое загрузки или обработки

### Workspace (WRKS)

- [ ] **WRKS-01**: Пользователь видит список записей в sidebar и может переключаться между ними
- [ ] **WRKS-02**: Пользователь задаёт вопрос по записи и получает ответ с цитатой в чате
- [ ] **WRKS-03**: Пользователь запускает быстрый анализ (summary/тезисы/action items/FAQ) из правой панели
- [ ] **WRKS-04**: Пользователь просматривает диаризованную транскрипцию (спикер → реплика) в правой панели
- [ ] **WRKS-05**: Трёхколоночный layout с collapsible панелями

### Scaffold (SCAF)

- [ ] **SCAF-01**: React + Vite + TypeScript проект с shadcn/ui инициализирован и запускается в Docker
- [ ] **SCAF-02**: Маршрутизация работает: `/` → загрузка, `/recordings/:id/processing` → ожидание, `/recordings/:id` → workspace
- [ ] **SCAF-03**: API layer с двумя Axios инстансами (data_ingress + llm_analysis) через Vite proxy

## v2 Requirements

Deferred to future release.

### Расширенный анализ

- **ANLZ-06**: Регенерация результата анализа (кнопка "сгенерировать заново")
- **ANLZ-07**: Конспект по темам (структурированный план лекции)
- **ANLZ-08**: Определения и термины
- **ANLZ-09**: Вопросы для самопроверки

### Аналитика диалога

- **DIAL-01**: Анализ участия спикеров (соотношение)
- **DIAL-02**: Тональность (sentiment) по сегментам
- **DIAL-03**: Тематическая сегментация (разбивка на блоки)

### Продвинутое

- **ADV-01**: Поиск по записям с цитатой и таймкодом
- **ADV-02**: Перевод конспекта на другой язык

### Авторизация

- **AUTH-01**: Регистрация и логин пользователей
- **AUTH-02**: Записи привязаны к конкретному пользователю

## Out of Scope

Explicitly excluded from all milestones.

| Feature | Reason |
|---------|--------|
| Auto-analysis после транскрипции | Сжигает токены на непросмотренные записи |
| SSE/WebSocket streaming ответов | Усложняет архитектуру; HTTP poll/wait достаточно |
| Fine-tuning моделей | Не нужен для типовых задач, GPT-4o-mini справляется |
| Live analysis (реальное время) | Нет live-транскрипции в пайплайне |
| Cross-recording comparison | Требует RAG инфраструктуру |
| Export в PDF/DOCX | Отдельная задача, не v1.1 |
| Audio playback | Не core value, большая фича |
| Batch upload | Один файл за раз достаточно |
| Dark/Light theme toggle | Cosmetic, не core |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BAPI-01 | Phase 5 | Pending |
| BAPI-02 | Phase 5 | Complete |
| BAPI-03 | Phase 5 | Pending |
| BAPI-04 | Phase 5 | Pending |
| BAPI-05 | Phase 5 | Complete |
| BAPI-06 | Phase 5 | Complete |
| SCAF-01 | Phase 6 | Pending |
| SCAF-02 | Phase 6 | Pending |
| SCAF-03 | Phase 6 | Pending |
| UPLD-01 | Phase 7 | Pending |
| UPLD-02 | Phase 7 | Pending |
| UPLD-03 | Phase 7 | Pending |
| UPLD-04 | Phase 7 | Pending |
| WRKS-01 | Phase 8 | Pending |
| WRKS-02 | Phase 8 | Pending |
| WRKS-03 | Phase 8 | Pending |
| WRKS-04 | Phase 8 | Pending |
| WRKS-05 | Phase 8 | Pending |

**Coverage:**
- v1.1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0

---
*Requirements defined: 2026-03-22 (v1.0), updated 2026-03-24 (v1.1)*
*Last updated: 2026-03-24 after roadmap creation*
