import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/weather_db")

settings = Settings()