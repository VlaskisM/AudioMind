from pydantic import BaseModel

from llm_analysis_service.src.services.models import (
    SummaryResult,
    KeyPointsResult,
    ActionItemsResult,
)


class SummaryResponse(BaseModel):
    """Response schema для POST /analysis/{recording_id}/summary."""

    status: str
    data: SummaryResult


class KeyPointsResponse(BaseModel):
    """Response schema для POST /analysis/{recording_id}/key-points."""

    status: str
    data: KeyPointsResult


class ActionItemsResponse(BaseModel):
    """Response schema для POST /analysis/{recording_id}/action-items."""

    status: str
    data: ActionItemsResult
