import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    environment: str = os.getenv("ENVIRONMENT", "development")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "True") == "True"
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")


settings = Settings()