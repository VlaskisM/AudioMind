from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.services.analysis import AnalysisService, AnalysisError
from src.web.schemas.analysis import (
    SummaryResponse,
    KeyPointsResponse,
    ActionItemsResponse,
    FaqResponse,
)
from src.web.dependencies import get_analysis_service
from src.web.dependencies.auth import get_current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{recording_id}/summary", response_model=SummaryResponse)
async def get_summary(
    recording_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: AnalysisService = Depends(get_analysis_service),
) -> SummaryResponse:
    """Получить краткое содержание записи."""
    try:
        result = await service.get_summary(recording_id)
        return SummaryResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{recording_id}/key-points", response_model=KeyPointsResponse)
async def get_key_points(
    recording_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: AnalysisService = Depends(get_analysis_service),
) -> KeyPointsResponse:
    """Получить ключевые тезисы записи с привязкой к спикерам."""
    try:
        result = await service.get_key_points(recording_id)
        return KeyPointsResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{recording_id}/action-items", response_model=ActionItemsResponse)
async def get_action_items(
    recording_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: AnalysisService = Depends(get_analysis_service),
) -> ActionItemsResponse:
    """Получить action items записи с ответственными."""
    try:
        result = await service.get_action_items(recording_id)
        return ActionItemsResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{recording_id}/faq", response_model=FaqResponse)
async def get_faq(
    recording_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: AnalysisService = Depends(get_analysis_service),
) -> FaqResponse:
    """Получить FAQ по содержанию записи."""
    try:
        result = await service.get_faq(recording_id)
        return FaqResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
