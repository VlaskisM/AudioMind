from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSSettings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost,http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        extra="ignore",
    )


cors_settings = CORSSettings()
