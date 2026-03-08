from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # MONGODB_URL: str
    # MONGODB_DATABASE: str

    POSTGRESS_USERNAME: str
    POSTGRESS_PASSWORD: str
    POSTGRESS_HOSTS: str
    POSTGRESS_PORT: int
    POSTGRESS_MAIN_DATABASE: str

    POSTGRESS_PDF_DATABASE:str
    

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

     # Optional legacy / not used
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # Ollama
    OLLAMA_API_URL: str
    OLLAMA_API_KEY: Optional[str] = None  # facultatif si pas utilisé
    GENERATION_MODEL_ID_LITERAL: List[str] = None
    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    # Generation defaults
    INPUT_DAFAULT_MAX_CHARACTERS: int
    GENERATION_DAFAULT_MAX_TOKENS: int
    GENERATION_DAFAULT_TEMPERATURE: float

    

    VECTOR_DB_BACKEND_LITERAL: List[str] = None
    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str = None
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100

    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()