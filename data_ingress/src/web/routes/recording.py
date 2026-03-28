from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from src.db.uow import UnitOfWork
from src.services.recording import RecordingService
from src.web.dependencies.auth import get_current_user
from src.web.mappers.recording import RecordingMapper
from src.web.schemas.recording import (
    RecordingCreate,
    RecordingResponse,
    PaginatedRecordingListResponse,
    StatusResponse,
    StatusUpdate,
)

service = RecordingService(uow_factory=UnitOfWork)
mapper = RecordingMapper()

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("/", response_model=PaginatedRecordingListResponse)
async def list_recordings(
    user_id: Annotated[int, Depends(get_current_user)],
    offset: int = 0,
    limit: int = 20,
):
    recordings, total = await service.get_recordings_page(offset, limit, user_id=user_id)
    return mapper.to_paginated_list_response(recordings, total, offset, limit)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RecordingResponse)
async def create_recording(
    body: RecordingCreate,
    user_id: Annotated[int, Depends(get_current_user)],
):
    recording = await service.create_recording(
        file_url=body.file_url,
        user_id=user_id,
    )
    return mapper.to_response(recording)


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=RecordingResponse)
async def upload_recording(
    user_id: Annotated[int, Depends(get_current_user)],
    file: UploadFile = File(...),
):
    recording = await service.upload_and_create_recording(
        user_id=user_id,
        file_obj=file.file,
        original_filename=file.filename,
    )
    return mapper.to_response(recording)


@router.get("/{recording_id}/status", response_model=StatusResponse)
async def get_recording_status(
    recording_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
):
    recording = await service.get_recording_status(recording_id)
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return mapper.to_status_response(recording)


@router.patch("/{recording_id}/status", response_model=StatusResponse)
async def update_recording_status(recording_id: int, body: StatusUpdate):
    try:
        recording = await service.update_recording_status(
            recording_id, body.status, body.error_message
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return mapper.to_status_response(recording)
