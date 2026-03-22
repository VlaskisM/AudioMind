import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from src.messaging.consumer import RabbitMQConsumer
from src.db.cloud_storage.s3 import S3Downloader
from src.db.mongodb import TranscriptionReader, TRANSCRIPTION_COLLECTION
from src.db.uow import UnitOfWork
from src.services.diarization import DiarizationService
from src.configs.mongodb import mongo_settings
from src.configs.huggingface import hf_settings

s3 = S3Downloader()
diarization_service = DiarizationService(hf_token=hf_settings.HF_TOKEN, device="cpu")

mongo_client = AsyncIOMotorClient(mongo_settings.url)
db = mongo_client[mongo_settings.MONGO_DB]
transcription_reader = TranscriptionReader(db[TRANSCRIPTION_COLLECTION])


async def process_message(body: dict) -> None:
    recording_id = body["recording_id"]
    audio_name = body["audio_name"]

    audio_path = await s3.download(audio_name)
    try:
        transcription = await transcription_reader.get(recording_id)
        segments = transcription["segments"] if transcription else []

        result = await asyncio.to_thread(diarization_service.diarize, str(audio_path), segments)

        async with UnitOfWork() as uow:
            inserted_id = await uow.diarizations.save(
                recording_id, result["speakers"], result["num_speakers"]
            )
            uow.track_insert(inserted_id)
            uow.publish(recording_id)
            await uow.commit()
    finally:
        audio_path.unlink(missing_ok=True)


async def main():
    consumer = RabbitMQConsumer(on_message=process_message)
    await consumer.start()
    await asyncio.Future()
