# Pitfalls Research: Speechmate v1.1 — Web Frontend

**Domain:** React SPA + Python microservices integration
**Date:** 2026-03-24
**Context:** Adding React frontend to existing platform (data_ingress:8001, llm_analysis_service:8003)

## Critical Pitfalls

### 1. CORS не настроен на FastAPI сервисах
- **Проблема:** React dev server (localhost:5173) → FastAPI (localhost:8001/8003) — браузер блокирует запросы
- **Признаки:** `Access-Control-Allow-Origin` ошибки в console, все запросы падают
- **Предотвращение:** Добавить `CORSMiddleware` на оба FastAPI сервиса сразу. В dev: `allow_origins=["http://localhost:5173"]`, в prod: конкретный домен
- **Фаза:** Backend API — первый шаг перед любым фронтендом

### 2. Polling не останавливается при unmount
- **Проблема:** Компонент Processing Screen размонтируется (юзер ушёл), но polling продолжает слать запросы
- **Признаки:** Memory leaks, "Can't perform state update on unmounted component", лишние запросы
- **Предотвращение:** TanStack Query автоматически отменяет запросы при unmount. НЕ использовать `setInterval` вручную
- **Фаза:** Processing Screen

### 3. Статус записи — нет state machine на бэкенде
- **Проблема:** Бэкенд не хранит текущий статус записи (uploaded/transcribing/diarizing/ready/failed). Фронтенду нечего поллить
- **Признаки:** Невозможно показать прогресс, фронтенд не знает когда запись готова
- **Предотвращение:** Добавить поле `status` в модель Recording (PostgreSQL). Обновлять при каждом событии RabbitMQ
- **Фаза:** Backend API — критический blocker

### 4. Два бэкенда — путаница с базовыми URL
- **Проблема:** Фронтенд обращается к data_ingress (загрузка, статус, список) И llm_analysis (анализ, чат). Легко перепутать
- **Признаки:** 404 ошибки, запросы идут не к тому сервису
- **Предотвращение:** Два Axios instance с чёткими именами (`ingressApi`, `analysisApi`). Vite proxy с разными prefix (`/api/ingress/*`, `/api/analysis/*`)
- **Фаза:** Frontend Foundation

### 5. File upload без progress indicator
- **Проблема:** Аудиофайлы большие (50-500MB). Без прогресса юзер думает что приложение зависло
- **Признаки:** Юзер закрывает вкладку во время загрузки
- **Предотвращение:** Axios `onUploadProgress` callback → progress bar. `multipart/form-data` с chunk upload для больших файлов
- **Фаза:** Upload Page

## Moderate Pitfalls

### 6. Трёхколоночный layout ломается на маленьких экранах
- **Проблема:** Sidebar + chat + right panel не помещаются на экранах < 1200px
- **Признаки:** Горизонтальный скролл, перекрытие панелей, нечитаемый текст
- **Предотвращение:** Collapsible sidebar и right panel. Tailwind responsive breakpoints. Минимальная ширина чата — 400px
- **Фаза:** Layout

### 7. Анализ results не обновляются при переключении записи
- **Проблема:** Юзер кликает другую запись в sidebar, но правая панель показывает анализы предыдущей записи
- **Признаки:** Стейл данные, путаница у пользователя
- **Предотвращение:** TanStack Query с `queryKey: ['analysis', recordingId, type]` — автоматическая инвалидация при смене recordingId
- **Фаза:** Workspace

### 8. Chat history загружается заново при каждом переключении
- **Проблема:** Переключился на другую запись → вернулся → чат загружается с нуля
- **Признаки:** Медленное переключение, мерцание UI
- **Предотвращение:** TanStack Query кэширует автоматически. `staleTime: 5 * 60 * 1000` для chat history
- **Фаза:** Chat

### 9. Длинная транскрипция в правой панели — виртуализация
- **Проблема:** 2000+ строк транскрипции рендерятся все сразу — тормоза
- **Признаки:** Lag при открытии таба транскрипции, зависание UI
- **Предотвращение:** CSS `overflow-y: auto` + `max-height` с нативным скроллом. Для 10000+ строк — виртуализация (@tanstack/react-virtual)
- **Фаза:** Transcript Viewer

### 10. Loading states — пустой экран вместо skeleton
- **Проблема:** Пока данные грузятся — пустой белый блок. Чувствуется медленно
- **Признаки:** "Почему ничего не происходит?"
- **Предотвращение:** shadcn/ui Skeleton компонент на каждом блоке. Loading state для каждого query
- **Фаза:** Все компоненты

### 11. Error boundary отсутствует
- **Проблема:** JS ошибка в одном компоненте крашит всё приложение
- **Признаки:** Белый экран
- **Предотвращение:** React Error Boundary на уровне layout, отдельные на sidebar/chat/right panel
- **Фаза:** Frontend Foundation

## Minor Pitfalls

### 12. Docker networking — фронтенд не видит бэкенд в Docker
- **Проблема:** В dev proxy работает (localhost), в Docker Compose нужны service names
- **Предотвращение:** В production: nginx reverse proxy перед фронтендом, проксирует `/api/*` к сервисам

### 13. Оптимистичный UI для чата
- **Проблема:** Отправил сообщение → ждёшь 5-15 сек ответа LLM → ничего не происходит
- **Предотвращение:** Сообщение юзера появляется мгновенно + typing indicator для ответа LLM

### 14. shadcn/ui темы — несовместимость с кастомными стилями
- **Проблема:** Кастомный CSS конфликтует с CSS variables shadcn/ui
- **Предотвращение:** Использовать только Tailwind utility classes. Не переопределять CSS variables shadcn

### 15. React Router — потеря state при refresh
- **Проблема:** Юзер на `/recordings/123`, нажал F5 → 404 или потеря стейта
- **Предотвращение:** Vite SPA fallback (`historyApiFallback`), state из URL params + TanStack Query кэш

### 16. Формат дат и имён записей
- **Проблема:** Запись называется `audio_2026-03-24_15-30.wav` — некрасиво в sidebar
- **Предотвращение:** Парсить имя файла, показывать дату в человеческом формате. Опционально: позволить переименование

---
*16 pitfalls identified, prioritized by impact on Speechmate v1.1 frontend*
*Researched: 2026-03-24*
