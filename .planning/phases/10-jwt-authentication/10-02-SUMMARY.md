---
phase: 10-jwt-authentication
plan: 02
subsystem: auth
tags: [jwt, pyjwt, fastapi, depends, oauth2, endpoint-protection]

# Dependency graph
requires:
  - phase: 10-jwt-authentication/01
    provides: get_current_user dependency, AuthSettings, OAuth2PasswordBearer in data_ingress
provides:
  - JWT-protected recording endpoints (GET list, POST create, POST upload, GET status)
  - Unprotected PATCH status endpoint for worker callbacks
  - User-scoped recording filtering by user_id from JWT
  - JWT validation in llm_analysis_service (AuthSettings + get_current_user)
  - Protected analysis, chat, and transcript endpoints in llm_analysis_service
affects: [10-03 frontend auth, future ownership checks in llm_analysis_service]

# Tech tracking
tech-stack:
  added: [pyjwt (llm_analysis_service)]
  patterns: [Annotated[int, Depends(get_current_user)] for JWT-protected endpoints, user_id passthrough to repository layer]

key-files:
  created:
    - llm_analysis_service/src/configs/auth.py
    - llm_analysis_service/src/web/dependencies/__init__.py
    - llm_analysis_service/src/web/dependencies/auth.py
  modified:
    - data_ingress/src/web/routes/recording.py
    - data_ingress/src/services/recording.py
    - data_ingress/src/db/relational/repositories/recording.py
    - data_ingress/src/repositories/recording.py
    - llm_analysis_service/src/web/routes/analysis.py
    - llm_analysis_service/src/web/routes/chat.py
    - llm_analysis_service/src/web/routes/transcript.py
    - llm_analysis_service/requirements.txt

key-decisions:
  - "dependencies.py converted to dependencies/ package in llm_analysis_service to co-locate auth.py -- existing imports preserved"
  - "tokenUrl in llm_analysis_service points to /api/ingress/auth/login (nginx path) for Swagger UI compatibility"
  - "nginx already covers /api/ingress/auth/ via prefix match -- no nginx changes needed"

patterns-established:
  - "Annotated[int, Depends(get_current_user)]: standard pattern for JWT-protected endpoints across all services"
  - "user_id passthrough: routes -> service -> repository for user-scoped queries"

requirements-completed: [AUTH-03, AUTH-04, AUTH-05, AUTH-06]

# Metrics
duration: 2min
completed: 2026-03-28
---

# Phase 10 Plan 02: Endpoint Protection Summary

**JWT protection on all public recording/analysis/chat/transcript endpoints with user-scoped recording filtering and unprotected worker callback**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-28T10:12:08Z
- **Completed:** 2026-03-28T10:14:11Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- All data_ingress recording endpoints protected with JWT (except PATCH status for worker callbacks)
- Recordings filtered by user_id from JWT token at repository level
- All llm_analysis_service endpoints (analysis, chat, transcript) protected with JWT
- JWT validation infrastructure created in llm_analysis_service (AuthSettings + get_current_user)

## Task Commits

Each task was committed atomically:

1. **Task 1: Protect data_ingress recordings + filter by user_id** - `1333948` (feat)
2. **Task 2: JWT validation in llm_analysis_service + nginx check** - `5350a2f` (feat)

## Files Created/Modified
- `data_ingress/src/repositories/recording.py` - Added user_id param to abstract get_page
- `data_ingress/src/db/relational/repositories/recording.py` - User-scoped filtering in get_page queries
- `data_ingress/src/services/recording.py` - Passthrough user_id to repository
- `data_ingress/src/web/routes/recording.py` - JWT dependency on all endpoints except PATCH status
- `llm_analysis_service/src/configs/auth.py` - AuthSettings reading JWT_SECRET from env
- `llm_analysis_service/src/web/dependencies/__init__.py` - Converted from dependencies.py to package
- `llm_analysis_service/src/web/dependencies/auth.py` - get_current_user JWT dependency
- `llm_analysis_service/src/web/routes/analysis.py` - JWT auth on 4 analysis endpoints
- `llm_analysis_service/src/web/routes/chat.py` - JWT auth on 3 chat endpoints
- `llm_analysis_service/src/web/routes/transcript.py` - JWT auth on transcript endpoint
- `llm_analysis_service/requirements.txt` - Added pyjwt>=2.8.0

## Decisions Made
- Converted `dependencies.py` to `dependencies/` package in llm_analysis_service to co-locate `auth.py` -- all existing imports `from src.web.dependencies import ...` preserved
- `tokenUrl` in llm_analysis_service set to `/api/ingress/auth/login` (nginx-routed path) so Swagger UI can locate login endpoint
- Confirmed nginx `/api/ingress/` prefix match already covers auth routes -- no nginx config changes needed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Converted dependencies.py to dependencies/ package**
- **Found during:** Task 2
- **Issue:** Plan specified creating `llm_analysis_service/src/web/dependencies/` directory with `__init__.py` and `auth.py`, but existing code used `dependencies.py` as a flat module
- **Fix:** Moved `dependencies.py` to `dependencies/__init__.py`, preserving all imports
- **Files modified:** llm_analysis_service/src/web/dependencies/__init__.py (renamed from dependencies.py)
- **Verification:** Import paths unchanged, all `from src.web.dependencies import ...` still work
- **Committed in:** 5350a2f (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary structural change to support auth.py co-location. No scope creep.

## Issues Encountered
- Task 2 commit included pre-existing uncommitted changes in dialogue_detection/ and transcription_service/ (Dockerfile and requirements.txt modifications for torch CPU index). These are out of scope but were already in the working tree.

## User Setup Required

None - JWT_SECRET must already be configured from Plan 01.

## Next Phase Readiness
- All public endpoints protected with JWT
- Ready for Plan 03 (frontend auth integration)
- llm_analysis_service does not yet verify recording ownership (noted in STATE.md blockers)

---
*Phase: 10-jwt-authentication*
*Completed: 2026-03-28*
