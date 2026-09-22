import warnings
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/science_pop"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    STORAGE_PATH: str = "./storage"

    COZE_API_URL: str = "https://api.coze.cn"
    # Never commit a real personal access token: set COZE_API_KEY in .env.
    COZE_API_KEY: str = ""
    COZE_GPT_WORKFLOW_ID: str = "7632694345599402024"
    COZE_BANANA_WORKFLOW_ID: str = "7632693911492771878"

    CRAWL_MAX_PAPERS_PER_SOURCE: int = 50
    CRAWL_USER_AGENT: str = "SciencePopBot/1.0"

    @model_validator(mode="after")
    def _warn_missing_coze_key(self):
        if not self.COZE_API_KEY:
            warnings.warn(
                "COZE_API_KEY is empty: workflow conversion runs will be skipped "
                "(set COZE_API_KEY in .env).",
                stacklevel=1,
            )
        return self

    @property
    def papers_dir(self) -> Path:
        return Path(self.STORAGE_PATH) / "papers"

    @property
    def content_dir(self) -> Path:
        return Path(self.STORAGE_PATH) / "content"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
