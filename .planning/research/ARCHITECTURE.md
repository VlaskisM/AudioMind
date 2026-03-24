# Architecture Research: Speechmate v1.1 — Web Frontend

**Domain:** React SPA integration with existing Python microservices
**Date:** 2026-03-24
**Context:** Adding frontend to 4 existing services (data_ingress:8001, transcription_service, dialogue_detection, llm_analysis_service:8003)

## Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     React SPA (Vite :5173)                       │
│                                                                   │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ Sidebar   │  │  Chat Panel  │  │  Right Panel              │  │
│  │ (history) │  │  (messages)  │  │  ├─ Analysis tabs         │  │
│  │           │  │  (input)     │  │  └─ Transcript viewer     │  │
│  └──────────┘  └──────────────┘  └───────────────────────────┘  │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐    │
│  │ Upload Page  │  │ Processing   │  │ Workspace Layout    │    │
│  │ (drag&drop)  │  │ (polling)    │  │ (3-column)          │    │
│  └─────────────┘  └──────────────┘  └─────────────────────┘    │
│                                                                   │
│  Shared: TanStack Query │ Zustand │ Axios instances │ Router    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │    Vite Dev Proxy        │
              │  /api/ingress → :8001    │
              │  /api/analysis → :8003   │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
    │data_ingr│      │llm_anal │      │  Nginx  │
    │ess:8001 │      │ysis:8003│      │  (prod) │
    │         │      │         │      │         │
    │Upload   │      │Analysis │      │Proxy +  │
    │Status   │      │Chat     │      │Static   │
    │List     │      │Transcript│     │Files    │
    └────┬────┘      └────┬────┘      └─────────┘
         │                │
    ┌────┴────┐      ┌────┴────┐
    │PostgreSQL│      │ MongoDB │
    │(metadata)│      │(content)│
    └─────────┘      └─────────┘
```

## Integration Pattern: Direct Calls (no API gateway)

Фронтенд обращается напрямую к двум сервисам через Vite proxy (dev) или Nginx (prod):

| Route prefix | Target | Endpoints |
|-------------|--------|-----------|
| `/api/ingress/*` | data_ingress:8001 | Upload, status, recordings list |
| `/api/analysis/*` | llm_analysis_service:8003 | Analysis, chat, transcript |

**Почему не API gateway:** Два сервиса, простая маршрутизация. Gateway — оверкилл на данном этапе.

## New Backend Endpoints Required

### data_ingress (port 8001)

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/recordings/{id}/status` | GET | Статус записи для polling | ⚠️ Требует новое поле `status` в модели Recording |
| `/recordings` | GET | Список записей с пагинацией | Для sidebar. `?limit=50&offset=0&sort=-created_at` |
| `/internal/recordings/{id}/status` | PATCH | Обновление статуса воркерами | transcription_service и dialogue_detection вызывают по HTTP callback |

### llm_analysis_service (port 8003) или data_ingress

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/recordings/{id}/transcript` | GET | Диаризованная транскрипция | Для правой панели. Формат: `[{speaker, text, start, end}]` |

## Critical Gap: Status Field

⚠️ **Recording модель в data_ingress НЕ имеет поля `status`.**

Нужно:
1. Добавить `status: str` в модель Recording (PostgreSQL)
2. Alembic миграция
3. Обновлять статус при каждом событии:
   - `uploaded` — после сохранения файла
   - `transcribing` — когда transcription_service начал обработку
   - `diarizing` — когда dialogue_detection начал обработку
   - `ready` — когда всё завершено
   - `failed` — при ошибке

**Стратегия обновления:** HTTP callback от воркеров к data_ingress. data_ingress — единственный владелец PostgreSQL.

## Status Propagation Flow

```
data_ingress                transcription_service       dialogue_detection
    │                              │                          │
    │ POST /recordings/upload      │                          │
    │ → status = "uploaded"        │                          │
    │ → publish to RabbitMQ        │                          │
    │                              │                          │
    │  PATCH /internal/.../status  │                          │
    │ ◄──── status="transcribing"  │                          │
    │                              │ (processing...)          │
    │  PATCH /internal/.../status  │                          │
    │ ◄──── status="transcribed"   │                          │
    │                              │ → publish to RabbitMQ    │
    │                              │                          │
    │  PATCH /internal/.../status  │                          │
    │ ◄──────────────────────────────── status="diarizing"    │
    │                              │                          │ (processing...)
    │  PATCH /internal/.../status  │                          │
    │ ◄──────────────────────────────── status="ready"        │
```

## Frontend Component Architecture

```
App
├── Router
│   ├── / → UploadPage
│   │   └── DropZone + UploadProgress
│   │
│   ├── /recordings/:id/processing → ProcessingPage
│   │   └── StatusSteps + PollingHook
│   │
│   └── /recordings/:id → WorkspacePage
│       ├── Sidebar (RecordingList)
│       ├── ChatPanel
│       │   ├── MessageList
│       │   └── ChatInput
│       └── RightPanel
│           ├── AnalysisTab (Summary | KeyPoints | ActionItems | FAQ)
│           └── TranscriptTab (DiarizedTranscript)
│
├── Providers
│   ├── QueryClientProvider (TanStack Query)
│   └── ThemeProvider (shadcn/ui)
│
└── Shared
    ├── api/ (axios instances, endpoints)
    ├── hooks/ (useRecordingStatus, useAnalysis, useChat)
    └── store/ (zustand: selectedRecording, panelStates)
```

## Data Flow Patterns

### Polling (Processing Screen)
```ts
// TanStack Query с автоматической остановкой
useQuery({
  queryKey: ['recording-status', id],
  queryFn: () => ingressApi.get(`/recordings/${id}/status`),
  refetchInterval: (query) =>
    query.state.data?.status === 'ready' ? false : 3000,
  // Автоматическая очистка при unmount
})
```

### Analysis (Right Panel)
```ts
// Mutation с автоматическим обновлением кэша
useMutation({
  mutationFn: (type) => analysisApi.post(`/recordings/${id}/analyze`, { type }),
  onSuccess: (data, type) =>
    queryClient.setQueryData(['analysis', id, type], data)
})
```

### Chat (Center Panel)
```ts
// Оптимистичный UI: сообщение юзера появляется сразу
useMutation({
  mutationFn: (message) => analysisApi.post(`/recordings/${id}/chat`, { message }),
  onMutate: (message) => {
    // Добавить сообщение юзера в кэш мгновенно
  }
})
```

## Build Order (suggested)

| Phase | Components | Depends on | Delivers |
|-------|-----------|------------|----------|
| 1. Backend API | Status field, PATCH callback, GET status/list/transcript, CORS | Existing services | Backend ready for frontend |
| 2. Frontend Scaffold | Vite project, routing, providers, API layer, layout shell | Phase 1 | Navigable app skeleton |
| 3. Upload + Processing | UploadPage, ProcessingPage, polling | Phase 1 + 2 | Upload → ready flow |
| 4. Workspace | Sidebar, ChatPanel, RightPanel (analyses + transcript) | Phase 1 + 2 + 3 | Full user experience |

**Ключевой принцип:** Каждая фаза — вертикальный срез (бэкенд + фронтенд), а не горизонтальный (весь бэкенд → весь фронтенд).

## Production Deployment

```yaml
# docker-compose addition
frontend:
  build: ./frontend
  ports: ["3000:80"]
  # Nginx serves static + proxies /api/*
```

Nginx конфиг:
- `/` → React SPA (static files)
- `/api/ingress/*` → data_ingress:8001
- `/api/analysis/*` → llm_analysis_service:8003

---
*Architecture designed for integration with existing Speechmate microservices*
*Researched: 2026-03-24*
