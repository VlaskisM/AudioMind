# Requirements: Speechmate

**Defined:** 2026-03-22
**Core Value:** Пользователь загружает аудио и получает структурированный анализ содержания через LLM

## v1 Requirements

Requirements for milestone v1.0 — LLM Analysis Service.

### Очистка (CLEAN)

- [x] **CLEAN-01**: badge_id удалён из модели Recording и всей цепочки data_ingress

### Инфраструктура (INFR)

- [x] **INFR-01**: LLM analysis service запускается как отдельный FastAPI-микросервис в Docker
- [x] **INFR-02**: Сервис корректно обрабатывает транскрипции длиннее 60 минут (chunking)
- [ ] **INFR-03**: Повторный запрос анализа возвращает кэшированный результат из MongoDB
- [x] **INFR-04**: Результаты анализа привязаны к конкретным спикерам из диаризации

### Анализ (ANLZ)

- [ ] **ANLZ-01**: Пользователь получает краткое содержание (summary) записи
- [ ] **ANLZ-02**: Пользователь получает список ключевых тезисов
- [ ] **ANLZ-03**: Пользователь получает action items с указанием ответственных
- [ ] **ANLZ-04**: Пользователь получает FAQ по материалу записи
- [ ] **ANLZ-05**: Каждый тип анализа доступен через отдельный API эндпоинт

### Чат (CHAT)

- [ ] **CHAT-01**: Пользователь может задать вопрос по записи и получить ответ с цитатой
- [ ] **CHAT-02**: История чат-сессии сохраняется в MongoDB

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

## Out of Scope

Explicitly excluded from all milestones.

| Feature | Reason |
|---------|--------|
| Фронтенд / веб-интерфейс | Отдельный проект, сейчас строим бэкенд |
| Auto-analysis после транскрипции | Сжигает токены на непросмотренные записи |
| SSE/WebSocket streaming ответов | Усложняет архитектуру; HTTP poll/wait достаточно |
| Fine-tuning моделей | Не нужен для типовых задач, GPT-4o-mini справляется |
| Live analysis (реальное время) | Нет live-транскрипции в пайплайне |
| Cross-recording comparison | Требует RAG инфраструктуру |
| Export в PDF/DOCX | Задача фронтенда |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLEAN-01 | Phase 1: Foundation | Complete |
| INFR-01 | Phase 1: Foundation | Complete |
| INFR-02 | Phase 1: Foundation | Complete |
| INFR-04 | Phase 1: Foundation | Complete |
| ANLZ-01 | Phase 2: Core Analysis | Pending |
| ANLZ-02 | Phase 2: Core Analysis | Pending |
| ANLZ-03 | Phase 2: Core Analysis | Pending |
| ANLZ-05 | Phase 2: Core Analysis | Pending |
| INFR-03 | Phase 2: Core Analysis | Pending |
| ANLZ-04 | Phase 3: FAQ | Pending |
| CHAT-01 | Phase 4: Chat with Transcript | Pending |
| CHAT-02 | Phase 4: Chat with Transcript | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after roadmap creation*
