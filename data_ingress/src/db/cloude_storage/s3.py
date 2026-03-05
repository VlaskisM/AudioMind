from abc import ABC, abstractmethod

import aioboto3

from src.configs.s3 import s3_settings


class S3UploaderBase(ABC):
    """Интерфейс S3-загрузчика (для подмены в тестах)."""

    @abstractmethod
    async def upload_file(self, file_obj, file_key: str) -> None:
        pass

    @abstractmethod
    async def get_file_url(self, file_key: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_key: str) -> None:
        pass


class AsyncS3Uploader(S3UploaderBase):
    def __init__(self):
        self.s3_url = s3_settings.s3_url
        self.s3_bucket = s3_settings.S3_BUCKET
        self.session = aioboto3.Session(
            aws_access_key_id=s3_settings.S3_ACCESS_KEY,
            aws_secret_access_key=s3_settings.S3_SECRET_KEY,
        )
        self.s3_client = None
        self._client_context = None

    async def connect(self):
        """Подключается к S3 и создаёт бакет если нужно."""
        self._client_context = self.session.client(
            "s3",
            endpoint_url=self.s3_url,
        )
        self.s3_client = await self._client_context.__aenter__()
        await self._ensure_bucket_exists()

    async def close(self):
        """Закрывает соединение с S3."""
        if self._client_context:
            await self._client_context.__aexit__(None, None, None)
            self.s3_client = None
            self._client_context = None

    async def _ensure_bucket_exists(self):
        """Создаёт бакет, если его ещё нет."""
        try:
            await self.s3_client.head_bucket(Bucket=self.s3_bucket)
        except Exception:
            await self.s3_client.create_bucket(Bucket=self.s3_bucket)

    async def upload_file(self, file_obj, file_key: str) -> None:
        await self.s3_client.upload_fileobj(
            file_obj,
            self.s3_bucket,
            file_key,
        )

    async def get_file_url(self, file_key: str) -> str:
        return await self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.s3_bucket, "Key": file_key},
        )

    async def delete_file(self, file_key: str) -> None:
        await self.s3_client.delete_object(Bucket=self.s3_bucket, Key=file_key)


