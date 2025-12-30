"""Configuration for the Agentic Seller POC."""
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Config(BaseModel):
    """Global configuration."""

    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    default_llm_model: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4-turbo-preview")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))

    # CRM Configuration
    hubspot_api_key: str = os.getenv("HUBSPOT_API_KEY", "")
    salesforce_api_key: str = os.getenv("SALESFORCE_API_KEY", "")

    # Memory Configuration
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"


# Global config instance
config = Config()
