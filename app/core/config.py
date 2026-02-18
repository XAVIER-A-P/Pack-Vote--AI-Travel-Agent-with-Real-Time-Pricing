from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str | None = None

    # AI Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    
    # Redis
    REDIS_URL: str

    class Config:
        env_file = ".env"
        case_sensitive = True

    # Auto-construct DB URI
    def __init__(self, **data):
        super().__init__(**data)
        self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()