import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_api_base: str | None = os.getenv("GEMINI_API_BASE") or "https://generativelanguage.googleapis.com/v1"
    claudia_api_key: str | None = os.getenv("CLAUDIA_API_KEY") or None

settings = Settings()