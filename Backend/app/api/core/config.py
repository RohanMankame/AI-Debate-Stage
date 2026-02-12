from pydantic import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()