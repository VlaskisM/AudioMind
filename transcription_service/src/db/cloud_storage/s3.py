import tempfile
from pathlib import Path

import aioboto3

from src.configs.s3 import s3_settings


class S3Downloader:

    def __init__(self):
        self._session = aioboto3.Session(
            aws_access_key_id=s3_settings.S3_ACCESS_KEY,
            aws_secret_access_key=s3_settings.S3_SECRET_KEY,
        )

    async def download(self, file_key: str) -> Path:
        suffix = Path(file_key).suffix or ".bin"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.close()
        tmp_path = Path(tmp.name)

        async with self._session.client("s3", endpoint_url=s3_settings.S3_ENDPOINT) as client:
            await client.download_file(s3_settings.S3_BUCKET, file_key, str(tmp_path))

        return tmp_path
