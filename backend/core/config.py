from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://vos:vos@localhost:5432/vos"
    redis_url: str = "redis://localhost:6379"
    
    # Git/Docs
    repos_base_path: str = "/repos"
    
    # AI Providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    
    # App
    debug: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
