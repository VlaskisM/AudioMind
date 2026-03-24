from src.db.relational.entities.recording import Recording
from src.web.schemas.recording import (
    RecordingResponse,
    RecordingListResponse,
    RecordingStatusData,
    StatusResponse,
    PaginatedRecordingListResponse,
)


class RecordingMapper:

    @staticmethod
    def to_response(recording: Recording) -> RecordingResponse:
        return RecordingResponse.model_validate(recording)

    @staticmethod
    def to_list_response(recordings: list[Recording]) -> RecordingListResponse:
        return RecordingListResponse(
            data=[RecordingResponse.model_validate(r) for r in recordings]
        )

    @staticmethod
    def to_status_response(recording: Recording) -> StatusResponse:
        return StatusResponse(
            status="ok",
            data=RecordingStatusData.model_validate(recording),
        )

    @staticmethod
    def to_paginated_list_response(
        recordings: list[Recording], total: int, offset: int, limit: int
    ) -> PaginatedRecordingListResponse:
        return PaginatedRecordingListResponse(
            data=[RecordingResponse.model_validate(r) for r in recordings],
            total=total,
            offset=offset,
            limit=limit,
        )
