from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str

    db_connection: str
    db_host: str
    db_port: int
    db_database: str
    db_username: str
    db_password: str

    text_embedding_model: str = "text-embedding-004"
    agent_model: str = "gemini-3-flash-preview"
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-3-flash-preview"

    prompt_dir: str = 'app/prompts'
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    graph_storage_path: str = "./data/graphs"
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = Settings()
