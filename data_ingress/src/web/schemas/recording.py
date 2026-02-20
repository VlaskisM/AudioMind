from pydantic import BaseModel


class RecordingCreate(BaseModel):
    badge_id: str
    ts: int
    file_url: str
    user_id: int


class RecordingResponse(BaseModel):
    id: int
    badge_id: str
    ts: int
    file_url: str
    user_id: int

    model_config = {"from_attributes": True}
