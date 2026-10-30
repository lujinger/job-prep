from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 优先读系统环境变量，其次读 .env，都没有则用下方默认值
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 环境变量大小写不敏感，SECRET_KEY / secret_key 都能匹配
        extra="ignore",        # 忽略无关环境变量（如 PATH），避免启动报错
    )

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./bookmark.db"


settings = Settings()


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
PORT = settings.PORT
DATABASE_URL = settings.DATABASE_URL
