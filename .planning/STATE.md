---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: Infrastructure & UX
status: in-progress
last_updated: "2026-03-28T12:27:00.000Z"
progress:
  total_phases: 12
  completed_phases: 3
  total_plans: 24
  completed_plans: 10
---

# State: Speechmate

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-28)

**Core value:** Пользователь загружает аудио и получает структурированный анализ содержания через LLM
**Current focus:** Phase 11 — UX Redesign

## Current Position

Phase: 12 of 12 (Unit Tests)
Plan: 2 of 2 in current phase -- COMPLETE
Status: Phase 12 Plan 02 Complete
Last activity: 2026-03-28 — Completed 12-02 (RecordingRepository + AuthService unit tests)

Progress: [████████████████████] 100% (24/24 plans completed)

## Performance Metrics

**Velocity:**
- Total plans completed: 23 (v1.0: 8, v1.1: 8, v1.2: 5, v1.3: 2)
- Average duration: ~30 min
- Total execution time: ~8 hours

**Recent Trend:**
- Stable velocity across milestones

## Accumulated Context

### Decisions

- transcription_service и dialogue_detection: UoW не нужен — одна атомарная запись в MongoDB
- data_ingress: UoW оправдан — распределённая транзакция (S3 + PostgreSQL + RabbitMQ)
- GigaChat возвращает plain text вместо JSON — нужен retry/парсинг в llm_client
- Docker: transcription и dialogue_detection сервисы работают на CPU (нет GPU)
- Nginx: CORS только в FastAPI, не в nginx (избежать дублирования заголовков)
- JWT: worker status callback исключён из защиты (внутренний эндпоинт)
- JWT: user_id FK на recordings — omit в v1.2, добавить в v1.3
- [Phase 09]: Keep http://localhost:5173 in CORS for backward compatibility with direct Vite dev server
- [Phase 10-01]: AuthService uses session_factory injection (not UoW) -- single atomic write per operation
- [Phase 10-01]: Login endpoint accepts JSON body (not OAuth2PasswordRequestForm) -- better for SPA frontend
- [Phase 10-02]: dependencies.py converted to dependencies/ package in llm_analysis_service for auth.py co-location
- [Phase 10-02]: tokenUrl in llm_analysis_service points to /api/ingress/auth/login (nginx path) for Swagger UI
- [Phase 10-02]: nginx /api/ingress/ prefix match already covers auth routes -- no config changes needed
- [Phase 10-03]: JWT sub claim uses string (not int) per RFC 7519
- [Phase 10-03]: Logout button added to sidebar and upload page for UX completeness
- [Phase 10-03]: Removed hardcoded ?user_id=1 from upload -- user_id from JWT
- [Phase 11-01]: shadcn base-nova uses @base-ui/react Dialog (not Radix)
- [Phase 11-01]: UploadModal rendered inside Sidebar -- portal handles positioning
- [Phase 11-02]: HoverCard used instead of Tooltip for processing status -- avoids sidebar tooltip conflicts
- [Phase 12-01]: pytest-asyncio 0.24.0 with asyncio_mode=auto for data_ingress tests
- [Phase 12-01]: publish() mocked as sync MagicMock, publisher.publish() as async -- matches real impl
- [Phase 12-02]: MagicMock(spec=Recording) instead of Recording.__new__ -- SQLAlchemy instrumented attributes need mapper init
- [Phase 12-02]: AuthService tests patch at src.services.auth.UserRepository and src.services.auth.password_hash

### Pending Todos

None yet.

### Blockers/Concerns

- Existing recordings с user_id=1 нужно мигрировать при добавлении auth
- llm_analysis_service в v1.2 валидирует JWT, но не проверяет ownership записи

## Session Continuity

Last session: 2026-03-28
Stopped at: Completed 12-02-PLAN.md (RecordingRepository + AuthService unit tests)
Resume file: None
