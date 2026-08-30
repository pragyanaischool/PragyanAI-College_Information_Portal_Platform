"""
src/core/config.py

Pydantic-based centralized settings management for PragyanAI College Intelligence Hub.
Loads environment variables, manages filesystem directories, defines database parameters,
sets up LLM inference keys (Groq / OpenAI / Custom Endpoints), and configures retrieval thresholds.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Automatically locate the repository root folder
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """System-wide configuration settings with environment overrides."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application Metadata ---
    APP_NAME: str = "PragyanAI College Intelligence Hub"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="production", validation_alias="ENVIRONMENT")
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    SECRET_KEY: str = Field(
        default="pragyanai-enterprise-session-secret-key-2026-v1",
        validation_alias="SECRET_KEY",
    )

    # --- Filesystem Directory Paths ---
    BASE_DIR: Path = ROOT_DIR
    DATA_DIR: Path = ROOT_DIR / "data"
    RAW_DATA_DIR: Path = ROOT_DIR / "data" / "raw"
    BROCHURES_DIR: Path = ROOT_DIR / "data" / "raw" / "brochures"
    PRESENTATIONS_DIR: Path = ROOT_DIR / "data" / "raw" / "presentations"
    REGULATORY_DIR: Path = ROOT_DIR / "data" / "raw" / "regulatory"
    SEED_DIR: Path = ROOT_DIR / "data" / "seed"
    VECTOR_STORE_DIR: Path = ROOT_DIR / "data" / "vector_store"

    # --- Relational Database Settings (SQLite / PostgreSQL) ---
    DATABASE_URL: str = Field(
        default=f"sqlite:///{ROOT_DIR / 'pragyanai_college_hub.db'}",
        validation_alias="DATABASE_URL",
    )
    DB_ECHO_SQL: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # --- LLM Provider & Inference Engine ---
    GROQ_API_KEY: str = Field(default="", validation_alias="GROQ_API_KEY")
    GROQ_MODEL_NAME: str = Field(
        default="llama3-70b-8192",
        validation_alias="GROQ_MODEL_NAME",
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = Field(default=None, validation_alias="OPENAI_BASE_URL")
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_RETRIES: int = 3
    LLM_TIMEOUT_SECONDS: int = 30

    # --- Vector Database & Embedding Models ---
    CHROMA_PERSIST_DIRECTORY: str = str(ROOT_DIR / "data" / "vector_store")
    CHROMA_COLLECTION_NAME: str = "pragyanai_college_docs"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 4

    # --- Web Search & External Tool API Keys ---
    TAVILY_API_KEY: Optional[str] = Field(default=None, validation_alias="TAVILY_API_KEY")
    SERPAPI_API_KEY: Optional[str] = Field(default=None, validation_alias="SERPAPI_API_KEY")

    # --- Admission Intelligence & Scoring Parameters ---
    DEFAULT_ACADEMIC_YEAR: int = 2026
    MAX_QUALIFYING_RANK: int = 185000
    HIGH_INTENT_LEAD_THRESHOLD: int = 4  # Scale: 1 (Cold) to 5 (Urgent/High-Priority)
    SUPER_DREAM_CTC_THRESHOLD_LPA: float = 25.0
    MEDIAN_ROI_PAYBACK_MONTHS_BENCHMARK: int = 24

    # --- Streamlit Server Configuration ---
    STREAMLIT_SERVER_PORT: int = 8501
    STREAMLIT_SERVER_ADDRESS: str = "0.0.0.0"

    def ensure_directories(self) -> None:
        """Verifies and creates all data and asset storage directories securely."""
        for path in [
            self.DATA_DIR,
            self.RAW_DATA_DIR,
            self.BROCHURES_DIR,
            self.PRESENTATIONS_DIR,
            self.REGULATORY_DIR,
            self.SEED_DIR,
            self.VECTOR_STORE_DIR,
        ]:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create directory {path}: {e}")


# Singleton settings instance initialized for the entire application lifecycle
settings = Settings()
settings.ensure_directories()
