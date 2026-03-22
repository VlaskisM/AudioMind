---
phase: 02-core-analysis
plan: 02
subsystem: api
tags: [fastapi, lifespan, analysis-service, caching, endpoints]

# Dependency graph
requires:
  - phase: 02-core-analysis
    provides: Pydantic models, prompts, LLMClient with map-reduce, AnalysisRepository
provides:
  - AnalysisService orchestrating cache -> diarization -> chunking -> LLM -> save pipeline
  - FastAPI lifespan initializing all dependencies into app.state
  - POST endpoints for summary, key-points, action-items with caching
  - Response schemas (SummaryResponse, KeyPointsResponse, ActionItemsResponse)
affects: [03-faq-generation, 04-chat]

# Tech tracking
tech-stack:
  added: []
  patterns: [lifespan-dependency-injection, app-state-service-access, cache-first-pipeline]

key-files:
  created:
    - llm_analysis_service/src/services/analysis.py
    - llm_analysis_service/src/web/routes/analysis.py
    - llm_analysis_service/src/web/schemas/analysis.py
  modified:
    - llm_analysis_service/src/app.py
    - llm_analysis_service/src/web/web.py

key-decisions:
  - "app.state for service injection (no Depends() DI -- simpler for singleton services)"
  - "AnalysisError -> 404, RuntimeError -> 502 error mapping in endpoints"
  - "Cache-first pipeline: check MongoDB before calling LLM"

patterns-established:
  - "Lifespan pattern: init services in lifespan, store in app.state, access via request.app.state"
  - "Cache-first analysis: get_cached() -> LLM -> save() with upsert"
  - "Error hierarchy: AnalysisError (data missing) vs RuntimeError (LLM failure)"

requirements-completed: [ANLZ-01, ANLZ-02, ANLZ-03, ANLZ-05, INFR-03]

# Metrics
duration: 2min
completed: 2026-03-22
---

# Phase 2 Plan 2: Analysis Service, Lifespan and API Endpoints Summary

**AnalysisService with cache-first pipeline, FastAPI lifespan for dependency init, and POST endpoints for summary/key-points/action-items**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T11:18:05Z
- **Completed:** 2026-03-22T11:20:30Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- AnalysisService orchestrating full pipeline: cache check -> diarization data -> chunking -> LLM map-reduce -> cache save
- FastAPI lifespan initializing MongoDBClient, LLMClient, readers, repositories, and services with proper shutdown
- Three POST endpoints with error handling (404 for missing data, 502 for LLM errors)
- Response schemas consistent with existing BaseResponse pattern (status + data)

## Task Commits

Each task was committed atomically:

1. **Task 1: AnalysisService and response schemas** - `8ec33c5` (feat)
2. **Task 2: Lifespan, API endpoints and wiring** - `f305b5c` (feat)

## Files Created/Modified
- `llm_analysis_service/src/services/analysis.py` - AnalysisService with _run_analysis() common pipeline and three public methods
- `llm_analysis_service/src/web/schemas/analysis.py` - SummaryResponse, KeyPointsResponse, ActionItemsResponse
- `llm_analysis_service/src/app.py` - FastAPI lifespan with full dependency initialization and cleanup
- `llm_analysis_service/src/web/routes/analysis.py` - POST endpoints for /analysis/{recording_id}/summary, /key-points, /action-items
- `llm_analysis_service/src/web/web.py` - Updated with lifespan and analysis router

## Decisions Made
- app.state for service injection -- simpler than FastAPI Depends() for singleton services initialized once at startup
- AnalysisError -> 404, RuntimeError -> 502 -- clear error mapping for different failure modes
- Cache-first pipeline avoids redundant LLM calls for repeated analysis requests

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Core analysis API complete -- all three analysis types available via REST endpoints
- Phase 02 fully delivered: building blocks (Plan 01) + orchestration + API (Plan 02)
- Ready for Phase 03 (FAQ Generation) and Phase 04 (Chat) which depend on Phase 02

---
*Phase: 02-core-analysis*
*Completed: 2026-03-22*
