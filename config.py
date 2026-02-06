"""Configuration module for the Medical Voice Assistant."""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""

    # Telegram Bot Configuration
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Groq AI Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

    # Salute Speech Recognition Configuration
    SALUTE_SPEECH_TOKEN: str = os.getenv("SALUTE_SPEECH_TOKEN", "")
    SALUTE_SPEECH_URL: str = "https://smartspeech.sber.ru/rest/v1/speech:recognize"

    # Audio Processing Configuration
    FFMPEG_PATH: Optional[str] = os.getenv("FFMPEG_PATH")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp_audio")
    MAX_AUDIO_DURATION: int = int(os.getenv("MAX_AUDIO_DURATION", "300"))  # 5 minutes

    # Application Configuration
    MAX_SUMMARY_LENGTH: int = int(os.getenv("MAX_SUMMARY_LENGTH", "1500"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration parameters.

        Returns:
            list[str]: List of missing or invalid configuration variables.
        """
        missing_vars = []
        required_vars = ["TELEGRAM_TOKEN", "GROQ_API_KEY", "SALUTE_SPEECH_TOKEN"]

        for var_name in required_vars:
            value = getattr(cls, var_name, "")
            if not value:
                missing_vars.append(var_name)

        return missing_vars

    @classmethod
    def is_valid(cls) -> bool:
        """Check if all required configuration variables are present.

        Returns:
            bool: True if all required variables are present, False otherwise.
        """
        return len(cls.validate()) == 0