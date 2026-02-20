from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.relational.db import get_session
from src.db.relational.repositories.recording import RecordingRepository
from src.web.schemas.recording import RecordingCreate, RecordingResponse

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("/", response_model=list[RecordingResponse])
async def get_all_recordings(session: AsyncSession = Depends(get_session)):
    repo = RecordingRepository(session)
    return await repo.get_all()


@router.post("/", response_model=RecordingResponse, status_code=201)
async def create_recording(
    data: RecordingCreate,
    session: AsyncSession = Depends(get_session),
):
    repo = RecordingRepository(session)
    return await repo.create(
        badge_id=data.badge_id,
        ts=data.ts,
        file_url=data.file_url,
        user_id=data.user_id,
    )
