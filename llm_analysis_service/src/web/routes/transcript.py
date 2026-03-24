from fastapi import APIRouter, Depends, HTTPException

from llm_analysis_service.src.db.mongodb.diarization_reader import DiarizationReader
from llm_analysis_service.src.web.schemas.transcript import TranscriptResponse, TranscriptSegment
from llm_analysis_service.src.web.dependencies import get_diarization_reader

router = APIRouter(prefix="/analysis/recordings", tags=["transcript"])


@router.get("/{recording_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(
    recording_id: int,
    diarization_reader: DiarizationReader = Depends(get_diarization_reader),
):
    """Получить диаризованную транскрипцию записи."""
    speakers = await diarization_reader.get_speakers(recording_id)
    if not speakers:
        raise HTTPException(status_code=404, detail="Transcript not found")

    segments = []
    for speaker in speakers:
        for seg in speaker["segments"]:
            segments.append(TranscriptSegment(
                speaker=speaker["label"],
                start=seg["start"],
                end=seg["end"],
                text=seg["text"],
            ))
    segments.sort(key=lambda s: s.start)

    return TranscriptResponse(recording_id=recording_id, segments=segments)
