from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    speaker: str
    start: float
    end: float
    text: str


class TranscriptResponse(BaseModel):
    recording_id: int
    segments: list[TranscriptSegment]
