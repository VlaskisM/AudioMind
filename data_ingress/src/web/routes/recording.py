from fastapi import APIRouter

from src.services.recording import RecordingService
from src.web.schemas.recording import RecordingCreate, RecordingResponse

router = APIRouter(prefix="/recordings", tags=["recordings"])
service = RecordingService()


@router.get("/", response_model=list[RecordingResponse])
async def get_all_recordings():
    return await service.get_all()


@router.post("/", response_model=RecordingResponse, status_code=201)
async def create_recording(data: RecordingCreate):
    return await service.create(data)
