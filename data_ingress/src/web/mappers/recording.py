from src.db.relational.entities.recording import Recording
from src.web.schemas.recording import RecordingResponse, RecordingListResponse


class RecordingMapper:

    @staticmethod
    def to_response(recording: Recording) -> RecordingResponse:
        return RecordingResponse.model_validate(recording)

    @staticmethod
    def to_list_response(recordings: list[Recording]) -> RecordingListResponse:
        return RecordingListResponse(
            data=[RecordingResponse.model_validate(r) for r in recordings]
        )
