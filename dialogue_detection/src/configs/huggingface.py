from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class HuggingFaceSettings(BaseSettings):
    HF_TOKEN: str

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent.parent / ".env", extra="ignore")

hf_settings = HuggingFaceSettings()
