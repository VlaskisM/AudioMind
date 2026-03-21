import whisperx
from whisperx.diarize import DiarizationPipeline


class DiarizationService:

    def __init__(self, hf_token: str, device: str = "cpu"):
        self._pipeline = DiarizationPipeline(token=hf_token, device=device)

    def diarize(self, audio_path: str, transcription_segments: list[dict]) -> dict:
        audio = whisperx.load_audio(audio_path)
        diarize_segments = self._pipeline(audio)

        result = whisperx.assign_word_speakers(diarize_segments, {"segments": transcription_segments})

        speaker_segments: dict[str, list[dict]] = {}
        for seg in result["segments"]:
            speaker = seg.get("speaker", "UNKNOWN")
            if speaker not in speaker_segments:
                speaker_segments[speaker] = []
            speaker_segments[speaker].append({
                "start": round(seg["start"], 3),
                "end": round(seg["end"], 3),
                "text": seg.get("text", ""),
            })

        speakers = [
            {"label": speaker, "segments": segments}
            for speaker, segments in speaker_segments.items()
        ]

        return {"speakers": speakers, "num_speakers": len(speakers)}
