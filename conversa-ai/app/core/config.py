"""
Centraliza todas las variables de entorno del sistema usando Pydantic Settings.
Provee un singleton `settings` importable desde cualquier módulo.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada de ConversaAI.

    Carga las variables desde el archivo .env y valida tipos automáticamente.
    Las variables sin valor por defecto son obligatorias y lanzan un error
    descriptivo si no están presentes al iniciar la app.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App 
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "ConversaAI Analyzer"

    # Database (PostgreSQL)
    DATABASE_URL: str

    # AI & NLP (Groq & LangChain)
    GROQ_API_KEY: str = ""
    LLM_MODEL_NAME: str = "llama-3.1-70b-versatile"
    CEREBRAS_API_KEY: str = ""
    CEREBRAS_MODEL_NAME: str = "llama3.1-8b"

    # Observability (LangSmith)
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "conversa-ai-project"



    # ChromaDB
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000

    # Security
    SECRET_KEY: str = "change-me-in-production"

    @property
    def async_database_url(self) -> str:
        """Convierte la URL de PostgreSQL a formato async (asyncpg)."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Retorna una instancia cacheada (singleton) de Settings."""
    return Settings()


settings = get_settings()
