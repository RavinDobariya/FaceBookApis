from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Doc Management API"
    ENV: str = "dev"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str


    DATABASE_URL: str

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
