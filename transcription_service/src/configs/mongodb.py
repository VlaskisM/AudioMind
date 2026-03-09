from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBSettings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str

    @property
    def url(self) -> str:
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent.parent / ".env", extra="ignore")

mongo_settings = MongoDBSettings()
