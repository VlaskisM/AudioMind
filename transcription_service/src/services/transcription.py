import whisperx


class TranscriptionService:

    def __init__(self, model_name: str = "small", device: str = "cpu", compute_type: str = "int8"):
        self._model = whisperx.load_model(model_name, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> dict:
        audio = whisperx.load_audio(audio_path)
        result = self._model.transcribe(audio)

        segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
            for seg in result.get("segments", [])
        ]
        full_text = " ".join(seg["text"] for seg in segments)

        return {"text": full_text, "segments": segments}
