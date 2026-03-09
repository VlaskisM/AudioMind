import asyncio

from src.messaging.consumer import RabbitMQConsumer
from src.db.cloud_storage.s3 import S3Downloader
from src.services.transcription import TranscriptionService
from src.db.mongodb import TranscriptionRepository

s3 = S3Downloader()
repo = TranscriptionRepository()
whisper = TranscriptionService()


async def process_message(body: dict) -> None:
    recording_id = body["recording_id"]
    audio_name = body["audio_name"]

    audio_path = await s3.download(audio_name)
    try:
        result = whisper.transcribe(str(audio_path))
        await repo.save(recording_id, result["text"], result["segments"])
    finally:
        audio_path.unlink(missing_ok=True)


async def main():
    consumer = RabbitMQConsumer(on_message=process_message)
    await consumer.start()
    await asyncio.Future()
