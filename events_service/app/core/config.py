from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ERP Events Microservice"
    VERSION: str = "1.0.0"
    
    REDIS_URL: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()