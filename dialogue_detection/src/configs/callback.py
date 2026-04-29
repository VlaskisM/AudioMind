from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class CallbackSettings(BaseSettings):
    DATA_INGRESS_URL: str = "http://audiomind-app:8000"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        extra="ignore",
    )


callback_settings = CallbackSettings()
