from src.db.relational.entities.recording import Recording
from src.web.schemas.recording import RecordingResponse


class RecordingMapper:

    @staticmethod
    def to_response(recording: Recording) -> RecordingResponse:
        return RecordingResponse.model_validate(recording)

    @staticmethod
    def to_response_list(recordings: list[Recording]) -> list[RecordingResponse]:
        return [RecordingResponse.model_validate(r) for r in recordings]
