# Speechmate

## What This Is

Speechmate -- приложение для работы с аудиозаписями. Сервис data_ingress предоставляет REST API для CRUD-операций с recordings (badge, timestamp, file URL, user). Построен на FastAPI + SQLAlchemy async + PostgreSQL. Продукт на ранней стадии -- детали бизнес-логики будут уточнены позже.

## Core Value

Правильная архитектурная основа с самого начала -- чистые абстракции, dependency injection, слоистая структура, шаблон для масштабирования на новые сущности.

## Requirements

### Validated

- Recording CRUD (create, get_all, get_by_id, get_by_user_id, get_by_badge_id, delete) -- existing
- REST API endpoints (GET /recordings, POST /recordings) -- existing
- PostgreSQL через async SQLAlchemy + asyncpg -- existing
- Pydantic schemas для валидации запросов/ответов -- existing
- Abstract repository pattern (базовый, ABC + конкретная реализация в одном файле) -- existing
- Mapper layer (entity -> response schema) -- existing
- Alembic для миграций БД -- existing

### Active

- [ ] Вынести абстрактные репозитории в отдельный слой `src/repositories/`
- [ ] DI через конструктор сервисов (сервис принимает `AbstractRecordingRepository`)
- [ ] Ручная сборка зависимостей в роутах (`service = RecordingService(RecordingRepository())`)
- [ ] Установить этот паттерн как шаблон для всех будущих сущностей

### Out of Scope

- DI-контейнер (dishka, dependency-injector) -- ручная сборка достаточна на текущем этапе
- Новые бизнес-фичи -- фокус на архитектуре
- Аутентификация/авторизация -- будет позже
- Логирование -- будет позже

## Context

- Существующий код: один сервис `data_ingress` с единственной сущностью `Recording`
- Текущая проблема: `AbstractRecordingRepository` и `RecordingRepository` живут в одном файле внутри `db/relational/repositories/`; сервис сам создает конкретный репо вместо получения через DI
- Mapper layer уже выделен в `src/web/mappers/`
- Docker Compose для PostgreSQL 17
- Карта кодовой базы: `.planning/codebase/`

## Constraints

- **Tech stack**: Python + FastAPI + SQLAlchemy async + PostgreSQL -- уже выбрано и используется
- **Структура**: Монорепо с сервисом `data_ingress/` как подпроектом
- **Миграции**: Alembic с синхронным psycopg драйвером

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Абстракции репо в `src/repositories/` | Отделяет контракт от реализации, сервисный слой не зависит от инфраструктуры | -- Pending |
| DI через конструктор, без контейнера | Простота; контейнер добавить позже при необходимости | -- Pending |
| Сборка зависимостей в роутах | Composition root на уровне HTTP-слоя; прозрачно, легко отследить | -- Pending |

---
*Last updated: 2026-02-26 after initialization*
