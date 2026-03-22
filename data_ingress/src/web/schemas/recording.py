from pydantic import BaseModel


class RecordingCreate(BaseModel):
    file_url: str
    user_id: int


class RecordingResponse(BaseModel):
    id: int
    ts: int
    file_url: str
    user_id: int

    model_config = {"from_attributes": True}


class RecordingListResponse(BaseModel):
    data: list[RecordingResponse]
