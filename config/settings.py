# config/settings.py
# ============================================================
# Centralised settings — loaded once, imported everywhere.
# All values read from .env or environment variables.
# ============================================================

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application-wide settings loaded from .env"""

    # --- PostgreSQL ---
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="bi_platform", alias="DB_NAME")
    db_user: str = Field(default="bi_user", alias="DB_USER")
    db_password: str = Field(default="password", alias="DB_PASSWORD")
    database_url: str = Field(
        default="postgresql://bi_user:password@localhost:5432/bi_platform",
        alias="DATABASE_URL",
    )

    # --- OpenAI ---
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # --- Kafka ---
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS"
    )
    kafka_topic_sales: str = Field(default="sales_events", alias="KAFKA_TOPIC_SALES")
    kafka_topic_customers: str = Field(
        default="customer_events", alias="KAFKA_TOPIC_CUSTOMERS"
    )
    kafka_topic_inventory: str = Field(
        default="inventory_events", alias="KAFKA_TOPIC_INVENTORY"
    )

    # --- FastAPI ---
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_secret_key: str = Field(default="dev-secret", alias="API_SECRET_KEY")

    # --- Streamlit ---
    streamlit_port: int = Field(default=8501, alias="STREAMLIT_PORT")

    # --- Data Generator ---
    data_output_dir: str = Field(default="./data/raw", alias="DATA_OUTPUT_DIR")
    records_per_run: int = Field(default=1000, alias="RECORDS_PER_RUN")
    streaming_interval_seconds: int = Field(
        default=2, alias="STREAMING_INTERVAL_SECONDS"
    )

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: str = Field(default="./logs", alias="LOG_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance (loaded once at startup)."""
    return Settings()


# Convenience singleton
settings = get_settings()
