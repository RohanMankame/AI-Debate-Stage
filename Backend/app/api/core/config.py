from typing import Optional
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()