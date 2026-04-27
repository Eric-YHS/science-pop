from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/science_pop"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    STORAGE_PATH: str = "./storage"

    COZE_API_URL: str = "https://api.coze.cn"
    COZE_API_KEY: str = "pat_UTeXr5027tzFPbwCskDAsquBNGmF3RS2q6e3Eust78DYAMjKjNZLPfGzgUlJBjZi"
    COZE_GPT_WORKFLOW_ID: str = "7632694345599402024"
    COZE_BANANA_WORKFLOW_ID: str = "7632693911492771878"

    CRAWL_MAX_PAPERS_PER_SOURCE: int = 50
    CRAWL_USER_AGENT: str = "SciencePopBot/1.0"

    @property
    def papers_dir(self) -> Path:
        return Path(self.STORAGE_PATH) / "papers"

    @property
    def content_dir(self) -> Path:
        return Path(self.STORAGE_PATH) / "content"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
