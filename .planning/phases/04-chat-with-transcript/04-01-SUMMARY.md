---
phase: 04-chat-with-transcript
plan: 01
subsystem: api
tags: [openai, pydantic, mongodb, tiktoken, chat, structured-output]

requires:
  - phase: 02-core-analysis
    provides: "LLMClient, ChunkingService, DiarizationReader, AnalysisError"
provides:
  - "ChatAnswer Pydantic model (answer + quote)"
  - "CHAT_SYSTEM_PROMPT for transcript-based chat"
  - "LLMClient.chat_structured() for multi-turn messages"
  - "ChatSessionRepository for MongoDB chat history"
  - "ChatService.ask() orchestrating full chat pipeline"
affects: [04-chat-with-transcript]

tech-stack:
  added: []
  patterns: [token-budget-management, atomic-push-upsert, multi-turn-structured-output]

key-files:
  created:
    - llm_analysis_service/src/db/mongodb/chat_session_repository.py
    - llm_analysis_service/src/services/chat.py
  modified:
    - llm_analysis_service/src/services/models.py
    - llm_analysis_service/src/services/prompts.py
    - llm_analysis_service/src/services/llm_client.py
    - llm_analysis_service/src/db/mongodb/__init__.py

key-decisions:
  - "Token budget 128K context - 4K reserve; system+transcript always preserved, history trimmed from oldest"
  - "One chat session per recording (unique index on recording_id)"

patterns-established:
  - "Token budget management: system+question always fit, history trimmed newest-first"
  - "Atomic $push upsert for chat message persistence"

requirements-completed: [CHAT-01, CHAT-02]

duration: 2min
completed: 2026-03-22
---

# Phase 04 Plan 01: Chat Service and Data Layer Summary

**ChatService with token budget management, ChatSessionRepository with atomic $push, and LLMClient.chat_structured() for multi-turn structured output**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T12:04:05Z
- **Completed:** 2026-03-22T12:06:07Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- ChatAnswer model with answer + quote fields for structured chat responses
- CHAT_SYSTEM_PROMPT instructing LLM to answer only from transcript content
- LLMClient.chat_structured() accepting arbitrary messages array for multi-turn chat
- ChatSessionRepository with atomic $push upsert and unique recording_id index
- ChatService.ask() orchestrating full pipeline: transcript -> history -> token budget -> LLM -> save
- Token budget management trimming old history messages while preserving transcript and current question

## Task Commits

Each task was committed atomically:

1. **Task 1: ChatAnswer model, system prompt, chat_structured()** - `97b027a` (feat)
2. **Task 2: ChatSessionRepository and ChatService with token budget** - `4bfc7c4` (feat)

## Files Created/Modified
- `llm_analysis_service/src/services/models.py` - Added ChatAnswer(answer, quote) model
- `llm_analysis_service/src/services/prompts.py` - Added CHAT_SYSTEM_PROMPT
- `llm_analysis_service/src/services/llm_client.py` - Added chat_structured() method
- `llm_analysis_service/src/db/mongodb/chat_session_repository.py` - New: chat history CRUD with atomic $push
- `llm_analysis_service/src/db/mongodb/__init__.py` - Export ChatSessionRepository
- `llm_analysis_service/src/services/chat.py` - New: ChatService with token budget management

## Decisions Made
- Token budget: 128K context limit - 4K response reserve; system prompt + transcript always preserved, history trimmed from oldest to newest
- One chat session per recording (unique MongoDB index on recording_id)
- History messages stored with timestamp but sent to OpenAI without it (API doesn't accept extra fields)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ChatService ready for wiring into FastAPI endpoints (Plan 04-02)
- ChatSessionRepository.ensure_indexes() needs to be called at app startup
- ChatService depends on existing DiarizationReader and ChunkingService instances

## Self-Check: PASSED

All 6 files found. Both task commits (97b027a, 4bfc7c4) verified.

---
*Phase: 04-chat-with-transcript*
*Completed: 2026-03-22*
