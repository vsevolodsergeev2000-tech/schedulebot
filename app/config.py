from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite+aiosqlite:///reminders.db"
    TIMEZONE: str = "UTC"

    class Config:
        env_file = ".env"

settings = Settings()