import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator
import warnings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/todo_db"

    # OpenRouter API settings
    OPENROUTER_API_KEY: str

    # Model settings
    OPENROUTER_MODEL: str = "openai/gpt-4o"

    @field_validator("OPENROUTER_API_KEY")
    @classmethod
    def validate_openrouter_api_key(cls, v: str) -> str:
        if not v:
            raise ValueError("OPENROUTER_API_KEY is missing or empty!")

        # Check if it's a placeholder (common patterns for placeholders)
        placeholder_patterns = [
            "YOUR_OPENROUTER_API_KEY",
            "sk-or-v1-placeholder",  # Example placeholder format
            "your-openrouter-api-key",
            "{OPENROUTER_API_KEY}",
            "OPENROUTER_API_KEY",
            "sk-or-v1-" + "x" * 32,  # Common placeholder length
            "<<ENTER_YOUR_OPENROUTER_API_KEY_HERE>>",  # Your specific placeholder
        ]

        # Strip whitespace and check if it matches any placeholder pattern
        clean_value = v.strip()

        for pattern in placeholder_patterns:
            if clean_value == pattern:
                raise ValueError(f"OPENROUTER_API_KEY contains a placeholder value: {pattern}")

        # Additional validation for actual OpenRouter key format
        # OpenRouter keys typically start with "sk-or-v1-" followed by hex characters
        if clean_value.startswith("sk-or-v1-"):
            # Check if the rest of the key looks like a valid hex string
            key_part = clean_value[9:]  # Remove "sk-or-v1-" prefix
            if len(key_part) != 64:  # OpenRouter keys are typically 64 hex chars
                warnings.warn("OpenRouter API key may have unexpected length")

            # Check if key part consists of valid hex characters
            try:
                int(key_part, 16)  # Validate hex format
            except ValueError:
                raise ValueError("OPENROUTER_API_KEY format is invalid - not a valid hex string")
        else:
            # If it doesn't start with expected prefix, it's likely invalid
            raise ValueError("OPENROUTER_API_KEY does not have the expected 'sk-or-v1-' prefix")

        return clean_value

    model_config = {"env_file": ".env", "extra": "ignore", "case_sensitive": True}

# Create global settings instance
settings = Settings()

if __name__ == "__main__":
    print("Settings loaded successfully!")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"OpenRouter API Key: {'VALID' if settings.OPENROUTER_API_KEY else 'INVALID'}")
    print(f"OpenRouter Model: {settings.OPENROUTER_MODEL}")