from src.web.schemas.common import BaseResponse
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return BaseResponse(status="ok", message="Service is running")