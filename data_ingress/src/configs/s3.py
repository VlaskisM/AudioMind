from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_ENDPOINT: str
    S3_PORT: int

    @property
    def s3_url(self) -> str:
        return self.S3_ENDPOINT

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent.parent / ".env", extra="ignore")

s3_settings = S3Settings()
