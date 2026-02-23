from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "NDA Generator & Tracker"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'nda_generator.db'}"
    templates_dir: Path = BASE_DIR / "app" / "templates"
    output_dir: Path = BASE_DIR / "data" / "generated"

    model_config = {"env_prefix": "NDA_", "env_file": ".env"}


settings = Settings()
