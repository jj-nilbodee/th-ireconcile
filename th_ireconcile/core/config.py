"""
Environment configuration for the integrated Reflex application.
Uses pydantic for validation and type safety.
"""

import logging
from functools import lru_cache
from typing import Any, List

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings class that uses Pydantic for validation.
    Loads configuration from environment variables.
    """

    # Project metadata
    PROJECT_NAME: str = "iReconcile"
    PROJECT_DESCRIPTION: str = "Text extraction and comparison tool using Azure OCR"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Azure OCR Configuration
    AZURE_OCR_API_KEY: str = Field(default="", description="Azure OCR API key")
    AZURE_OCR_ENDPOINT: HttpUrl = Field(
        default="https://api.cognitive.microsofttranslator.com",
        description="Azure OCR API endpoint",
    )

    # Azure Blob Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = Field(
        default="", description="Azure Blob Storage connection string"
    )
    AZURE_STORAGE_CONTAINER_NAME: str = Field(
        default="uploads", description="Azure Blob Storage container name"
    )

    # CORS settings
    CORS_ORIGINS: List[str] = Field(default=["*"])

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if v is None:
            return ["*"]
        if isinstance(v, str):
            if v.strip() == "":
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                # Handle JSON-formatted string array
                try:
                    import json

                    return json.loads(v)
                except Exception as e:
                    logger.error(f"Error parsing CORS_ORIGINS JSON: {str(e)}")
                    # If JSON parsing fails, fall back to comma separation
                    v = v.strip("[]")
            # Handle comma-separated string
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    # Temp uploaded files directory
    UPLOAD_DIR: str = Field(
        default="uploads", description="Directory for temporary uploads"
    )

    # Configure environment file loading
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton with caching for efficiency.
    """
    return Settings()


# Create settings instance for easier importing
settings = get_settings()
