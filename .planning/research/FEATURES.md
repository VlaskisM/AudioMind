# Features Research: Speechmate v1.1 — Web Frontend

**Domain:** ChatGPT-like audio analysis web interface
**Date:** 2026-03-24
**Competitors analyzed:** Otter.ai, Fireflies.ai, Fathom, tl;dv, Granola, ChatGPT (UI patterns)

## Table Stakes (must have — 8 features)

Без этих функций продукт ощущается сломанным.

### 1. Upload Page (загрузка аудио)
- **Что:** Drag & drop зона + file picker для аудиофайлов
- **Ожидаемое поведение:** Визуальная обратная связь при drag-over, валидация типа файла, прогресс загрузки
- **Сложность:** Low
- **Зависимости:** Существующий `POST /recordings/upload` в data_ingress
- **Библиотеки:** react-dropzone

### 2. Processing Status Screen (экран ожидания)
- **Что:** Отображение прогресса транскрипции/диаризации
- **Ожидаемое поведение:** Шаги (uploading → transcribing → diarizing → ready), polling каждые 3-5 сек, автопереход в workspace при ready
- **Сложность:** Medium-High (state machine, polling cleanup on unmount)
- **Зависимости:** ⚠️ НОВЫЙ эндпоинт `GET /recordings/{id}/status` — НЕ СУЩЕСТВУЕТ
- **Библиотеки:** TanStack Query (refetchInterval)

### 3. Recording History Sidebar (сайдбар записей)
- **Что:** Список всех записей слева, как чаты в ChatGPT
- **Ожидаемое поведение:** Название/дата, текущая запись выделена, клик переключает workspace
- **Сложность:** Low-Medium
- **Зависимости:** ⚠️ НОВЫЙ эндпоинт `GET /recordings` (список с пагинацией) — НЕ СУЩЕСТВУЕТ

### 4. Chat Interface (чат по записи)
- **Что:** Центральная панель — input + сообщения (как ChatGPT)
- **Ожидаемое поведение:** Ввод вопроса → ответ с цитатой из транскрипции, история сохраняется
- **Сложность:** Medium
- **Зависимости:** Существующие `POST /recordings/{id}/chat`, `GET /recordings/{id}/chat/history`

### 5. Analysis Panel (панель быстрых анализов)
- **Что:** Правая панель с кнопками: Summary, Тезисы, Action Items, FAQ
- **Ожидаемое поведение:** Клик → запрос анализа, результат кэшируется, повторный клик → мгновенно из кэша
- **Сложность:** Low-Medium
- **Зависимости:** Существующие POST эндпоинты анализа в llm_analysis_service

### 6. Diarized Transcript Viewer (просмотр транскрипции)
- **Что:** Таб в правой панели — кто что сказал
- **Ожидаемое поведение:** Speaker labels + текст реплик, скролл по длинным записям
- **Сложность:** Low-Medium
- **Зависимости:** ⚠️ НОВЫЙ эндпоинт для чтения транскрипции/диаризации — НЕ СУЩЕСТВУЕТ

### 7. Error States (обработка ошибок)
- **Что:** Информативные ошибки на каждом шаге
- **Ожидаемое поведение:** Upload failed, transcription failed, LLM error — каждое с объяснением и retry
- **Сложность:** Low
- **Зависимости:** Все эндпоинты

### 8. Responsive Layout (ChatGPT-like)
- **Что:** Трёхколоночный layout: sidebar | chat | right panel
- **Ожидаемое поведение:** Панели collapsible, минимальная ширина для чата
- **Сложность:** Medium
- **Зависимости:** shadcn/ui + Tailwind

## Differentiators (конкурентное преимущество)

### 9. Markdown Rendering в ответах
- **Что:** LLM-ответы в чате и анализах рендерятся как markdown
- **Ожидаемое поведение:** Заголовки, списки, bold/italic, цитаты
- **Сложность:** Low (react-markdown)

### 10. Цитаты с attribution к спикеру
- **Что:** В ответах чата цитаты выделены и привязаны к конкретному спикеру
- **Сложность:** Medium (зависит от формата ответа LLM)

## Anti-Features (не делать в v1.1)

| Feature | Причина | Что делать вместо |
|---------|---------|-------------------|
| WebSocket/SSE для статуса | Сложнее, polling достаточно | TanStack Query polling |
| Audio playback | Не core value, большая фича | Просто текст транскрипции |
| Streaming LLM ответов | Backend не поддерживает SSE | Loading spinner |
| Batch upload | Один файл за раз достаточно для v1 | Последовательная загрузка |
| Search по записям | Требует полнотекстовый индекс | Простой список по дате |
| Export PDF/DOCX | Отдельная большая задача | Copy-to-clipboard |
| Авторизация | Отложена на v1.2 | Один пользователь |
| Dark/Light theme toggle | Cosmetic, не core | Один тёмный стиль (как GPT) |

## New Backend Endpoints Required

⚠️ **Эти 3 эндпоинта блокируют фронтенд:**

| Endpoint | Service | Purpose | Blocks |
|----------|---------|---------|--------|
| `GET /recordings/{id}/status` | data_ingress | Статус: uploaded/transcribing/diarizing/ready/failed | Processing screen |
| `GET /recordings` | data_ingress | Список записей с пагинацией | Sidebar |
| `GET /recordings/{id}/transcript` | llm_analysis_service или data_ingress | Диаризованная транскрипция | Transcript viewer |

## Feature Dependency Graph

```
Backend API (new endpoints)
    │
    ├── Upload Page ──── Processing Screen (polling status)
    │                        │
    │                        ▼
    │                    Workspace Layout
    │                    ┌──────────────────────────────┐
    │                    │ Sidebar │ Chat │ Right Panel  │
    │                    │         │      │ ├─ Analyses  │
    │                    │         │      │ └─ Transcript│
    │                    └──────────────────────────────┘
    │
    └── Error States (cross-cutting)
```

## Open Questions

- Какой формат у статуса записи? Нужна state machine: uploaded → transcribing → diarizing → ready | failed
- recording_id — UUID или MongoDB ObjectId? Влияет на роутинг
- Формат транскрипции для просмотра — raw WhisperX сегменты или нормализованный формат?

---
*Researched: 2026-03-24*
