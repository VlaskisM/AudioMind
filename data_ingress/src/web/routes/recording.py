from fastapi import APIRouter, UploadFile, File, status

from src.db.uow import UnitOfWork
from src.services.recording import RecordingService
from src.web.mappers.recording import RecordingMapper
from src.web.schemas.recording import (
    RecordingCreate,
    RecordingResponse,
    RecordingListResponse,
)

service = RecordingService(uow_factory=UnitOfWork)
mapper = RecordingMapper()

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("/", response_model=RecordingListResponse)
async def list_recordings():
    recordings = await service.get_all_recordings()
    return mapper.to_list_response(recordings)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RecordingResponse)
async def create_recording(body: RecordingCreate):
    recording = await service.create_recording(
        file_url=body.file_url,
        user_id=body.user_id,
    )
    return mapper.to_response(recording)


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=RecordingResponse)
async def upload_recording(
    user_id: int,
    file: UploadFile = File(...),
):
    recording = await service.upload_and_create_recording(
        user_id=user_id,
        file_obj=file.file,
        original_filename=file.filename,
    )
    return mapper.to_response(recording)
