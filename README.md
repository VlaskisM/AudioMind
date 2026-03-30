# Speechmate

Веб-приложение для автоматической транскрипции, диаризации и интеллектуального анализа аудиозаписей с помощью LLM.

Загрузите аудиофайл — система распознает речь, определит спикеров и сгенерирует краткое содержание, ключевые тезисы, action items и FAQ. Также доступен свободный чат по содержанию записи.

## Архитектура

Микросервисная архитектура с event-driven pipeline через RabbitMQ:

```
                         ┌──────────────┐
                         │   Frontend   │
                         │   (React)    │
                         └──────┬───────┘
                           HTTP │ HTTP
                    ┌──────────┴──────────┐
                    ▼                      ▼
            ┌──────────────┐     ┌──────────────────┐
            │ Data Ingress │     │  LLM Analysis    │
            │  (FastAPI)   │     │  (GigaChat)      │
            └──────┬───────┘     └────────┬─────────┘
                   │                      │
         ┌────────┼────────┐              │
         ▼        ▼        ▼              ▼
    PostgreSQL  MinIO   RabbitMQ       MongoDB
                (S3)       │
               ┌───────────┴───────────┐
               ▼                       ▼
    ┌───────────────────┐   ┌─────────────────────┐
    │   Transcription   │   │  Dialogue Detection  │
    │    (WhisperX)     │   │  (WhisperX Diarize)  │
    └─────────┬─────────┘   └──────────┬───────────┘
              ▼                        ▼
           MongoDB                  MongoDB
```

**Поток обработки:**
1. Пользователь загружает аудиофайл через frontend
2. **Data Ingress** сохраняет файл в S3 (MinIO), создаёт запись в PostgreSQL, публикует задачу в RabbitMQ
3. **Transcription Service** получает задачу, транскрибирует аудио через WhisperX, сохраняет результат в MongoDB
4. **Dialogue Detection** получает задачу, выполняет диаризацию спикеров, сохраняет в MongoDB
5. **LLM Analysis Service** по запросу пользователя анализирует транскрипцию через GigaChat

## Технологический стек

| Компонент | Технологии |
|-----------|-----------|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Query, Zustand, React Router |
| **Data Ingress** | Python 3.11, FastAPI, SQLAlchemy (async), asyncpg, Alembic, aioboto3, aio-pika |
| **Transcription** | Python 3.11, WhisperX, aio-pika, Motor (MongoDB), FFmpeg |
| **Dialogue Detection** | Python 3.11, WhisperX (diarization), PyTorch, aio-pika, Motor |
| **LLM Analysis** | Python 3.11, FastAPI, GigaChat SDK, Motor, tiktoken |
| **Инфраструктура** | Docker Compose, PostgreSQL 17, MongoDB 7, MinIO, RabbitMQ 3 |

## Быстрый старт

### Требования

- Docker и Docker Compose
- [HuggingFace токен](https://huggingface.co/settings/tokens) (для моделей диаризации)
- [GigaChat credentials](https://developers.sber.ru/portal/products/gigachat) (для LLM-анализа)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/VlaskisM/Speechmate.git
cd Speechmate
```

2. Создайте файл `.env` в корне проекта:
```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5434
DB_USER=speechmate
DB_PASSWORD=speechmate
DB_NAME=speechmate

# MinIO (S3)
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_PORT=9000
S3_BUCKET=recordings
S3_ENDPOINT=http://localhost:9000

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=audio_processing

# MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=speechmate

# Очереди
DIARIZATION_QUEUE=diarization_processing
NEXT_QUEUE=post_diarization_processing

# API ключи
HF_TOKEN=<ваш_huggingface_token>
GIGACHAT_CREDENTIALS=<ваши_gigachat_credentials_base64>
```

3. Запустите все сервисы:
```bash
docker compose up --build
```

4. Откройте в браузере: **http://localhost**

## Сервисы и порты

| Сервис | Порт | Назначение |
|--------|------|-----------|
| Nginx (точка входа) | [localhost](http://localhost) | Реверс-прокси: frontend, API |
| PostgreSQL | localhost:5434 | Метаданные записей |
| MongoDB | localhost:27017 | Транскрипции, диаризации, анализы |
| MinIO Console | [localhost:9002](http://localhost:9002) | Управление файловым хранилищем |
| RabbitMQ Management | [localhost:15672](http://localhost:15672) | Мониторинг очередей |

## API

Все API-запросы требуют JWT-токен в заголовке `Authorization: Bearer <token>`.

Маршрутизация через Nginx: `/api/ingress/*` → Data Ingress, `/api/analysis/*` → LLM Analysis.

### Data Ingress (`/api/ingress/recordings`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/recordings/upload` | Загрузка аудиофайла (multipart/form-data) |
| `GET` | `/recordings/?offset=0&limit=20` | Список записей с пагинацией |
| `GET` | `/recordings/{id}/status` | Статус обработки записи |
| `PATCH` | `/recordings/{id}/status` | Обновление статуса (callback от worker'ов) |
| `DELETE` | `/recordings/{id}` | Удаление записи (S3 + БД) |

**Статусы записи:** `uploaded` → `transcribing` → `diarizing` → `ready` / `failed`

### LLM Analysis (`/api/analysis/analysis`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/analysis/{id}/summary` | Краткое содержание |
| `POST` | `/analysis/{id}/key-points` | Ключевые тезисы |
| `POST` | `/analysis/{id}/action-items` | Задачи и действия |
| `POST` | `/analysis/{id}/faq` | Часто задаваемые вопросы |
| `POST` | `/analysis/{id}/chat` | Вопрос по содержанию записи |
| `GET` | `/analysis/{id}/chat/history` | История чата |
| `DELETE` | `/analysis/{id}/chat` | Очистка истории чата |
| `GET` | `/analysis/recordings/{id}/transcript` | Диаризованная транскрипция |

## Структура проекта

```
Speechmate/
├── data_ingress/              # API-сервис загрузки и управления записями
│   ├── src/
│   │   ├── configs/           # Настройки (DB, S3, RabbitMQ, CORS)
│   │   ├── db/                # PostgreSQL (SQLAlchemy), S3 (aioboto3)
│   │   ├── messaging/         # RabbitMQ publisher
│   │   ├── repositories/      # Repository pattern
│   │   ├── services/          # Бизнес-логика
│   │   └── web/               # FastAPI routes, schemas, mappers
│   └── migrations/            # Alembic миграции
│
├── transcription_service/     # Worker транскрипции (WhisperX)
│   └── src/
│       ├── configs/           # Настройки
│       ├── db/                # MongoDB, S3
│       ├── messaging/         # RabbitMQ consumer + publisher
│       └── services/          # Логика транскрипции
│
├── dialogue_detection/        # Worker диаризации спикеров
│   └── src/
│       ├── configs/           # Настройки + HuggingFace
│       ├── db/                # MongoDB, S3
│       ├── messaging/         # RabbitMQ consumer + publisher
│       └── services/          # Логика диаризации
│
├── llm_analysis_service/      # LLM-анализ через GigaChat
│   └── src/
│       ├── configs/           # Настройки GigaChat, MongoDB, CORS
│       ├── db/mongodb/        # Репозитории (анализы, чат, транскрипции)
│       ├── services/          # Map-reduce LLM, chunking, чат
│       └── web/               # FastAPI routes, schemas
│
├── frontend/                  # React веб-приложение
│   └── src/
│       ├── api/               # HTTP-клиенты (axios)
│       ├── components/        # UI компоненты + workspace
│       ├── hooks/             # React Query хуки
│       ├── pages/             # Страницы (Upload, Processing, Workspace)
│       └── stores/            # Zustand state management
│
├── docker-compose.yml         # Оркестрация всех сервисов
└── .env                       # Переменные окружения
```

## Поддерживаемые форматы

MP3, WAV, FLAC, OGG, M4A, WebM — до 500 МБ.
