import tomllib
from pathlib import Path
from typing import ClassVar, Literal

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

PYPROJECT_PATH = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _read_version() -> str:
    with PYPROJECT_PATH.open("rb") as f:
        return str(tomllib.load(f)["project"]["version"])


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    API_V1_STR: ClassVar[str] = "/api/v1"
    AUTH_STR: ClassVar[str] = "/auth"
    VERSION: ClassVar[str] = _read_version()

    PROJECT_NAME: str = "Solar Sensors"
    ENVIRONMENT: Literal["dev", "prod"] = "dev"

    PG_HOST: str
    PG_PORT: int = 5432
    PG_USER: str
    PG_PASSWORD: str = ""
    PG_DB: str = ""

    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="postgresql+psycopg",
                username=self.PG_USER,
                password=self.PG_PASSWORD,
                host=self.PG_HOST,
                port=self.PG_PORT,
                path=self.PG_DB,
            )
        )


settings = Settings()
