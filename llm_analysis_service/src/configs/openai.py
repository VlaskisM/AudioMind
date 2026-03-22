from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 4096

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent.parent / ".env", extra="ignore")

openai_settings = OpenAISettings()
