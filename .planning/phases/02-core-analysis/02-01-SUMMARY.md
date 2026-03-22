---
phase: 02-core-analysis
plan: 01
subsystem: api
tags: [openai, pydantic, structured-outputs, mongodb, llm]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: LLMClient with map-reduce, MongoDBClient, AsyncOpenAI wrapper
provides:
  - Pydantic models for OpenAI structured outputs (SummaryResult, KeyPointsResult, ActionItemsResult)
  - Prompts for map/reduce analysis (summary, key points, action items)
  - LLMClient.complete_structured() and map_reduce_structured() methods
  - AnalysisRepository for caching analysis results in MongoDB
affects: [02-core-analysis]

# Tech tracking
tech-stack:
  added: []
  patterns: [structured-outputs-via-parse, plain-text-map-structured-reduce, upsert-cache]

key-files:
  created:
    - llm_analysis_service/src/services/models.py
    - llm_analysis_service/src/services/prompts.py
    - llm_analysis_service/src/db/mongodb/analysis_repository.py
  modified:
    - llm_analysis_service/src/services/llm_client.py
    - llm_analysis_service/src/db/mongodb/__init__.py

key-decisions:
  - "Plain text on map phase, structured output on reduce phase only"
  - "RuntimeError for refusal/None parsed (not custom exception class)"
  - "datetime.now(timezone.utc) instead of deprecated datetime.utcnow()"

patterns-established:
  - "Structured outputs: beta.chat.completions.parse() with Pydantic response_format"
  - "Map-reduce structured: text intermediates, structured final result"
  - "MongoDB upsert cache: update_one with upsert=True on compound key"

requirements-completed: [ANLZ-01, ANLZ-02, ANLZ-03, INFR-03]

# Metrics
duration: 2min
completed: 2026-03-22
---

# Phase 2 Plan 1: Analysis Building Blocks Summary

**Pydantic structured output models, analysis prompts for 3 types, LLMClient with beta.chat.completions.parse(), AnalysisRepository with MongoDB upsert cache**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T11:14:01Z
- **Completed:** 2026-03-22T11:15:49Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Pydantic models (SummaryResult, KeyPointsResult, ActionItemsResult) ready for OpenAI structured outputs
- Six prompts (map+reduce for summary, key points, action items) with language-matching instruction
- LLMClient extended with complete_structured() and map_reduce_structured() methods
- AnalysisRepository with get_cached(), save() (upsert), ensure_indexes() for compound unique index

## Task Commits

Each task was committed atomically:

1. **Task 1: Pydantic-models structured outputs and prompts** - `5d89ae3` (feat)
2. **Task 2: LLMClient structured outputs + AnalysisRepository** - `e00b540` (feat)

## Files Created/Modified
- `llm_analysis_service/src/services/models.py` - Pydantic models for structured outputs (SummaryResult, KeyPoint, KeyPointsResult, ActionItem, ActionItemsResult)
- `llm_analysis_service/src/services/prompts.py` - Six prompts (map+reduce) for summary, key points, action items
- `llm_analysis_service/src/services/llm_client.py` - Extended with complete_structured(), map_reduce_structured(), model property
- `llm_analysis_service/src/db/mongodb/analysis_repository.py` - Repository with get_cached(), save() (upsert), ensure_indexes()
- `llm_analysis_service/src/db/mongodb/__init__.py` - Added AnalysisRepository export

## Decisions Made
- Plain text on map phase, structured output on reduce phase only -- avoids forcing intermediate results into final schema
- RuntimeError for refusal/None parsed responses -- simple, no custom exception class needed at this stage
- datetime.now(timezone.utc) instead of deprecated datetime.utcnow()

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All building blocks ready for AnalysisService orchestration (02-02)
- Models, prompts, LLM client methods, and repository are fully independent and testable

---
*Phase: 02-core-analysis*
*Completed: 2026-03-22*
