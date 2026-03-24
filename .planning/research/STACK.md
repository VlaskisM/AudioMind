# Stack Research: Speechmate v1.1 — Web Frontend

**Domain:** React SPA for audio analysis platform
**Date:** 2026-03-24
**Context:** Adding web frontend to existing Speechmate platform (4 Python microservices)

## New Libraries Required

| Library | Version | Purpose | Confidence |
|---------|---------|---------|------------|
| React + TypeScript | ^19 + ^5.5 | UI framework — зафиксировано в PROJECT.md | High |
| Vite | ^6 | Build tool, dev server с proxy к FastAPI | High |
| shadcn/ui + Tailwind CSS | latest CLI + ^4 | Component library (Radix UI primitives) | High |
| TanStack Query | ^5 | Server state, polling через `refetchInterval`, кэш | High |
| Axios | ^1.7 | HTTP-клиент к двум сервисам (data_ingress + llm_analysis) | High |
| Zustand | ^4.5 | UI state: выбранная запись, панели, sidebar | High |
| react-dropzone | ^14 | Drag & drop загрузка аудио | High |
| react-markdown | ^9 | Рендер LLM-ответов (markdown в чате) | Medium |
| React Router | ^6.26 | Маршрутизация: `/`, `/recordings/:id/processing`, `/recordings/:id` | High |

## What NOT to Add

| Library | Why Not |
|---------|---------|
| Next.js | SPA достаточно, SSR не нужен для внутреннего инструмента |
| Redux / MobX | Zustand покрывает нужды, Redux — overkill для этого масштаба |
| WebSocket libs | Polling выбран осознанно (проще, достаточно для статуса транскрипции) |
| Formik / react-hook-form | Одна форма загрузки — shadcn Input достаточно |
| Storybook | Не нужен на этом этапе |
| i18n | Один язык пока |
| SWR | TanStack Query мощнее — polling, mutations, devtools |

## Integration Points

### Vite Dev Proxy
```js
// vite.config.ts
proxy: {
  '/api/ingress': { target: 'http://localhost:8001' },
  '/api/analysis': { target: 'http://localhost:8003' }
}
```

### TanStack Query — Polling
```ts
useQuery({
  queryKey: ['recording-status', id],
  queryFn: () => getRecordingStatus(id),
  refetchInterval: (data) => data?.status === 'ready' ? false : 3000
})
```

### Axios Instances
Два отдельных инстанса с разными baseURL для data_ingress и llm_analysis_service.

### CORS
Настроить `CORSMiddleware` на обоих FastAPI сервисах для `http://localhost:5173` (Vite dev) и production origin.

## Warnings

- **Tailwind v4** вышел в феврале 2025 — проверить совместимость shadcn/ui CLI с v4 перед инициализацией
- **shadcn/ui** — не npm-пакет, а CLI-генератор: компоненты копируются в проект (`npx shadcn@latest add button`)
- **React 19** — проверить совместимость всех библиотек; если проблемы — откатиться на 18

---
*Confidence levels: High = proven in production, Medium = good evidence, Low = experimental*
*Researched: 2026-03-24*
