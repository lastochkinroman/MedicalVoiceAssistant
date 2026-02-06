"""Audio processing module for handling audio file operations."""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional

import aiofiles
import requests
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio file operations such as downloading, conversion, and validation."""

    @staticmethod
    async def download_telegram_audio(
        file_path: str, bot_token: str, save_path: str
    ) -> bool:
        """Download audio file from Telegram.

        Args:
            file_path: Telegram file path
            bot_token: Telegram bot token
            save_path: Local path to save the downloaded file

        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            async with aiofiles.open(save_path, "wb") as f:
                await f.write(response.content)

            logger.info(f"Audio downloaded successfully: {save_path}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading audio from Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during audio download: {e}")
            return False

    @staticmethod
    async def convert_to_speech_format(input_path: str, output_path: str) -> bool:
        """Convert audio file to WAV format suitable for speech recognition.

        Converts audio to 16kHz, mono, 16-bit PCM format.

        Args:
            input_path: Path to input audio file
            output_path: Path to save converted WAV file

        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            file_extension = Path(input_path).suffix.lower()

            if file_extension in [".ogg", ".oga"]:
                audio = AudioSegment.from_ogg(input_path)
            elif file_extension in [".mp3", ".m4a"]:
                audio = AudioSegment.from_mp3(input_path)
            elif file_extension == ".wav":
                audio = AudioSegment.from_wav(input_path)
            else:
                logger.error(f"Unsupported audio format: {file_extension}")
                return False

            # Convert to speech recognition format: 16kHz, mono, 16-bit PCM
            processed_audio = (
                audio.set_frame_rate(16000)
                .set_channels(1)
                .set_sample_width(2)
            )

            processed_audio.export(
                output_path,
                format="wav",
                parameters=["-acodec", "pcm_s16le"]
            )

            logger.info(f"Audio converted successfully: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return False

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Get duration of audio file in seconds.

        Args:
            file_path: Path to audio file

        Returns:
            float: Duration in seconds, 0 if error
        """
        try:
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000.0
            logger.debug(f"Audio duration: {duration:.1f} seconds")
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0

    @staticmethod
    def is_audio_valid(
        file_path: str, max_duration: int = 300
    ) -> Tuple[bool, str]:
        """Validate audio file for processing.

        Args:
            file_path: Path to audio file
            max_duration: Maximum allowed duration in seconds

        Returns:
            Tuple[bool, str]: (is_valid, validation_message)
        """
        if not os.path.exists(file_path):
            return False, "Файл не существует"

        duration = AudioProcessor.get_audio_duration(file_path)

        if duration == 0.0:
            return False, "Не удалось определить длительность аудио"

        if duration > max_duration:
            return (
                False,
                f"Аудио слишком длинное ({duration:.1f} сек). Максимум: {max_duration} сек"
            )

        if duration < 1.0:
            return False, "Аудио слишком короткое"

        return True, f"Аудио валидно, длительность: {duration:.1f} сек"