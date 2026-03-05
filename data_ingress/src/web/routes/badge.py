from fastapi import APIRouter, UploadFile, File, status

from src.db.uow import UnitOfWork
from src.services.recording import RecordingService
from src.web.mappers.recording import RecordingMapper
from src.web.schemas.recording import RecordingResponse

router = APIRouter(prefix="/badges", tags=["badges"])
service = RecordingService(UnitOfWork)
mapper = RecordingMapper()


@router.post("/{badge_id}/upload", status_code=status.HTTP_201_CREATED, response_model=RecordingResponse)
async def upload_badge_file(
    badge_id: str,
    user_id: int,
    file: UploadFile = File(...),
):
    recording = await service.upload_and_create_recording(
        badge_id=badge_id,
        user_id=user_id,
        file_obj=file.file,
        original_filename=file.filename,
    )
    return mapper.to_response(recording)
