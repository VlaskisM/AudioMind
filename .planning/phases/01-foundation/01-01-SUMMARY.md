---
phase: 01-foundation
plan: 01
subsystem: api
tags: [fastapi, sqlalchemy, alembic, cleanup]

# Dependency graph
requires: []
provides:
  - "Recording model without badge_id"
  - "POST /recordings/upload endpoint for file upload"
  - "Alembic migration drop_column badge_id"
affects: [01-foundation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-level service/mapper singletons in routes"

key-files:
  created:
    - "data_ingress/migrations/versions/a1b2c3d4e5f6_remove_badge_id_from_recordings.py"
  modified:
    - "data_ingress/src/db/relational/entities/recording.py"
    - "data_ingress/src/web/schemas/recording.py"
    - "data_ingress/src/repositories/recording.py"
    - "data_ingress/src/db/relational/repositories/recording.py"
    - "data_ingress/src/services/recording.py"
    - "data_ingress/src/web/routes/recording.py"
    - "data_ingress/src/web/web.py"

key-decisions:
  - "Kept String import in entity since file_url still uses it"
  - "Moved upload endpoint from badge route to POST /recordings/upload"

patterns-established:
  - "Upload via POST /recordings/upload with user_id query param and file multipart"

requirements-completed: [CLEAN-01]

# Metrics
duration: 2min
completed: 2026-03-22
---

# Phase 1 Plan 1: Remove badge_id Summary

**Complete removal of badge_id from data_ingress: entity, schemas, repositories, services, routes, plus Alembic migration and upload endpoint migration to /recordings/upload**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T10:38:58Z
- **Completed:** 2026-03-22T10:41:07Z
- **Tasks:** 2
- **Files modified:** 8 (7 modified, 1 created, 1 deleted)

## Accomplishments
- Removed badge_id from Recording entity, schemas, abstract/concrete repositories, and service layer
- Deleted badge.py route file and removed badge_router from FastAPI app
- Added POST /recordings/upload endpoint in recording routes (migrated from badge route)
- Created Alembic migration to drop badge_id column from recordings table

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove badge_id from entity, schemas, repositories and service** - `62cff86` (refactor)
2. **Task 2: Remove badge route, add upload endpoint, create migration** - `903cc73` (refactor)

## Files Created/Modified
- `data_ingress/src/db/relational/entities/recording.py` - Recording model without badge_id column
- `data_ingress/src/web/schemas/recording.py` - RecordingCreate and RecordingResponse without badge_id
- `data_ingress/src/repositories/recording.py` - Abstract repository without get_by_badge_id() and badge_id param
- `data_ingress/src/db/relational/repositories/recording.py` - Concrete repository without badge_id methods
- `data_ingress/src/services/recording.py` - Service methods without badge_id parameter
- `data_ingress/src/web/routes/recording.py` - Added POST /recordings/upload, updated POST /recordings/
- `data_ingress/src/web/web.py` - Removed badge_router inclusion
- `data_ingress/src/web/routes/badge.py` - DELETED
- `data_ingress/migrations/versions/a1b2c3d4e5f6_remove_badge_id_from_recordings.py` - Migration to drop badge_id column

## Decisions Made
- Kept String import in entity since file_url column still uses sa.String
- Moved file upload functionality from badge route (POST /badges/{badge_id}/upload) to recording route (POST /recordings/upload)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Restored String import in entity**
- **Found during:** Task 1 (Remove badge_id from entity)
- **Issue:** Removed String from sqlalchemy import thinking it was only for badge_id, but file_url also uses String
- **Fix:** Restored String to the import statement
- **Files modified:** data_ingress/src/db/relational/entities/recording.py
- **Verification:** File parses correctly with both Integer and String imported
- **Committed in:** 62cff86 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential fix for correctness. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- data_ingress codebase is clean of badge_id references
- Upload endpoint available at POST /recordings/upload
- Alembic migration ready to run against database
- Ready for subsequent foundation plans

## Self-Check: PASSED

All files verified present, all commits verified in git log, badge.py confirmed deleted.

---
*Phase: 01-foundation*
*Completed: 2026-03-22*
