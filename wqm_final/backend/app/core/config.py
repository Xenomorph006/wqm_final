from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # -------------------------
    # Application
    # -------------------------
    APP_NAME: str
    APP_VERSION: str

    HOST: str
    PORT: int

    # -------------------------
    # Model
    # -------------------------
    MODEL_PATH: str
    SCALER_PATH: str

    # -------------------------
    # CORS
    # -------------------------
    CORS_ORIGINS: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()