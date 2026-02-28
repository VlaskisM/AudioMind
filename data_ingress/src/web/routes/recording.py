from fastapi import APIRouter
from src.db.relational.repositories.recording import RecordingRepository
from src.services.recording import RecordingService
from src.web.mappers.recording import RecordingMapper
from src.web.schemas.recording import RecordingCreate, RecordingResponse

router = APIRouter(prefix="/recordings", tags=["recordings"])

service = RecordingService(RecordingRepository)
mapper = RecordingMapper()


@router.get("/", response_model=list[RecordingResponse])
async def get_all_recordings():
    recordings = await service.get_all()
    return mapper.to_response_list(recordings)


@router.post("/", response_model=RecordingResponse, status_code=201)
async def create_recording(data: RecordingCreate):
    recording = await service.create(data)
    return mapper.to_response(recording)
