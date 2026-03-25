from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class GigaChatSettings(BaseSettings):
    GIGACHAT_CREDENTIALS: str
    GIGACHAT_MODEL: str = "GigaChat"
    GIGACHAT_TEMPERATURE: float = 0.3
    GIGACHAT_MAX_TOKENS: int = 4096

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent.parent / ".env", extra="ignore")

gigachat_settings = GigaChatSettings()
