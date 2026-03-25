import asyncio

import httpx

from src.messaging.consumer import RabbitMQConsumer
from src.db.cloud_storage.s3 import S3Downloader
from src.services.transcription import TranscriptionService
from src.db.uow import UnitOfWork
from src.configs.callback import callback_settings

s3 = S3Downloader()
whisper = TranscriptionService()
http_client = httpx.AsyncClient(base_url=callback_settings.DATA_INGRESS_URL, timeout=10.0)


async def process_message(body: dict) -> None:
    recording_id = body["recording_id"]
    audio_name = body["audio_name"]

    # Статус: transcribing
    await http_client.patch(f"/recordings/{recording_id}/status", json={"status": "transcribing"})

    audio_path = await s3.download(audio_name)
    try:
        result = await asyncio.to_thread(whisper.transcribe, str(audio_path))

        async with UnitOfWork() as uow:
            inserted_id = await uow.transcriptions.save(recording_id, result["text"], result["segments"])
            uow.track_insert(inserted_id)
            uow.publish(recording_id, audio_name)
            await uow.commit()

        # Статус: diarizing (следующий этап)
        await http_client.patch(f"/recordings/{recording_id}/status", json={"status": "diarizing"})
    except Exception:
        # Статус: failed
        try:
            await http_client.patch(f"/recordings/{recording_id}/status", json={"status": "failed"})
        except Exception:
            pass  # Don't mask original error
        raise
    finally:
        audio_path.unlink(missing_ok=True)


async def main():
    consumer = RabbitMQConsumer(on_message=process_message)
    await consumer.start()
    await asyncio.Future()
