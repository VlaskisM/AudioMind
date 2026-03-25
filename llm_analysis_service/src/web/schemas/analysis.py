from pydantic import BaseModel

from src.services.models import (
    SummaryResult,
    KeyPointsResult,
    ActionItemsResult,
    FaqResult,
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


class FaqResponse(BaseModel):
    """Response schema для POST /analysis/{recording_id}/faq."""

    status: str
    data: FaqResult
