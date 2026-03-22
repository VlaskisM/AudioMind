from fastapi import APIRouter, Request, HTTPException

from llm_analysis_service.src.services.analysis import AnalysisService, AnalysisError
from llm_analysis_service.src.web.schemas.analysis import (
    SummaryResponse,
    KeyPointsResponse,
    ActionItemsResponse,
    FaqResponse,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _get_service(request: Request) -> AnalysisService:
    """Получить AnalysisService из app.state."""
    return request.app.state.analysis_service


@router.post("/{recording_id}/summary", response_model=SummaryResponse)
async def get_summary(recording_id: int, request: Request) -> SummaryResponse:
    """Получить краткое содержание записи."""
    try:
        result = await _get_service(request).get_summary(recording_id)
        return SummaryResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{recording_id}/key-points", response_model=KeyPointsResponse)
async def get_key_points(recording_id: int, request: Request) -> KeyPointsResponse:
    """Получить ключевые тезисы записи с привязкой к спикерам."""
    try:
        result = await _get_service(request).get_key_points(recording_id)
        return KeyPointsResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{recording_id}/action-items", response_model=ActionItemsResponse)
async def get_action_items(recording_id: int, request: Request) -> ActionItemsResponse:
    """Получить action items записи с ответственными."""
    try:
        result = await _get_service(request).get_action_items(recording_id)
        return ActionItemsResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{recording_id}/faq", response_model=FaqResponse)
async def get_faq(recording_id: int, request: Request) -> FaqResponse:
    """Получить FAQ по содержанию записи."""
    try:
        result = await _get_service(request).get_faq(recording_id)
        return FaqResponse(status="ok", data=result)
    except AnalysisError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
