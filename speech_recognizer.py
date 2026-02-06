"""Speech recognition module using Salute Speech API."""

import os
import uuid
import logging
from typing import Optional

import aiohttp
from config import Config

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Handles speech recognition using Salute Speech API."""

    def __init__(self):
        """Initialize the speech recognizer with configuration."""
        self.api_url = Config.SALUTE_SPEECH_URL
        self.token = Config.SALUTE_SPEECH_TOKEN

    async def recognize_speech(self, audio_file_path: str) -> Optional[str]:
        """Recognize speech from audio file.

        Args:
            audio_file_path: Path to WAV audio file

        Returns:
            Optional[str]: Recognized text or None if recognition failed
        """
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return None

            # Check file size (maximum 10MB)
            file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
            if file_size_mb > 10:
                logger.error(f"Audio file too large: {file_size_mb:.2f} MB")
                return None

            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()

            # Send request to Salute Speech API
            headers = {
                "Content-Type": "audio/x-pcm;bit=16;rate=16000",
                "Authorization": f"Bearer {self.token}",
                "X-Request-ID": str(uuid.uuid4()),
                "Accept": "application/json",
            }

            logger.info("Sending request to SaluteSpeech API...")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    data=audio_data,
                    ssl=False,  # Disable SSL verification (use with caution)
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

            if "result" in result:
                text = result["result"].strip()
                logger.info(f"Speech recognized: {len(text)} characters")
                return text
            else:
                logger.error(f"No 'result' field in response: {result}")
                return None

        except aiohttp.ClientError as e:
            logger.error(f"Network error in speech recognition: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}")
            return None

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize recognized text.

        Args:
            text: Raw recognized text

        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""

        # Remove extra whitespace
        cleaned_text = " ".join(text.split())

        # Common text corrections
        corrections = {
            "к примеру": "например",
            "спасибо большое": "спасибо",
            "пожалуйста большое": "пожалуйста",
        }

        for wrong, correct in corrections.items():
            cleaned_text = cleaned_text.replace(wrong, correct)

        logger.debug(f"Text cleaned: {cleaned_text[:200]}...")
        return cleaned_text