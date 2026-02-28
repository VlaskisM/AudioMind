from fastapi import APIRouter, status

from src.db.relational import db
from src.db.relational.repositories.recording import RecordingRepository
from src.services.recording import RecordingService
from src.web.mappers.recording import RecordingMapper
from src.web.schemas.recording import (
    RecordingCreate,
    RecordingResponse,
    RecordingListResponse,
)

router = APIRouter(prefix="/recordings", tags=["recordings"])
mapper = RecordingMapper()


@router.get("/", response_model=RecordingListResponse)
async def list_recordings():
    async with db.session() as session:
        service = RecordingService(RecordingRepository(session))
        recordings = await service.get_all_recordings()

    return mapper.to_list_response(recordings)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RecordingResponse)
async def create_recording(body: RecordingCreate):
    async with db.session() as session:
        service = RecordingService(RecordingRepository(session))

        recording = await service.create_recording(
            badge_id=body.badge_id,
            file_url=body.file_url,
            user_id=body.user_id,
        )

    return mapper.to_response(recording)
