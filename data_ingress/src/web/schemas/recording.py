from pydantic import BaseModel


class RecordingCreate(BaseModel):
    file_url: str
    user_id: int


class RecordingResponse(BaseModel):
    id: int
    ts: int
    file_url: str
    user_id: int
    status: str
    original_filename: str | None = None

    model_config = {"from_attributes": True}


class RecordingListResponse(BaseModel):
    data: list[RecordingResponse]


class RecordingStatusData(BaseModel):
    id: int
    status: str
    error_message: str | None = None

    model_config = {"from_attributes": True}


class StatusResponse(BaseModel):
    status: str
    data: RecordingStatusData


class StatusUpdate(BaseModel):
    status: str
    error_message: str | None = None


class PaginatedRecordingListResponse(BaseModel):
    data: list[RecordingResponse]
    total: int
    offset: int
    limit: int
