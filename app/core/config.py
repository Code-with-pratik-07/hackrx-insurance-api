from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str
    api_key: str = "hackrx_secret_key_123"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
