from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str
    openai_api_key: str

    # Database
    database_url: str
    supabase_url: str
    supabase_key: str

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # App Settings
    max_file_size_mb: int = 10
    free_tier_pdf_limit: int = 3
    free_tier_question_limit: int = 10

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
