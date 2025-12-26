import os
import aiofiles
import requests
from pathlib import Path
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    @staticmethod
    async def download_telegram_audio(file_path: str, bot_token: str, save_path: str) -> bool:
        try:
            url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(response.content)
            logger.info(f"Audio downloaded: {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return False

    @staticmethod
    async def convert_to_speech_format(input_path: str, output_path: str) -> bool:
        try:
            file_extension = Path(input_path).suffix.lower()
            if file_extension in ['.ogg', '.oga']:
                audio = AudioSegment.from_ogg(input_path)
            elif file_extension in ['.mp3', '.m4a']:
                audio = AudioSegment.from_mp3(input_path)
            elif file_extension == '.wav':
                audio = AudioSegment.from_wav(input_path)
            else:
                logger.error(f"Unsupported audio format: {file_extension}")
                return False
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)
            audio.export(
                output_path,
                format="wav",
                parameters=["-acodec", "pcm_s16le"]
            )
            logger.info(f"Audio converted: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return False

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0

    @staticmethod
    def is_audio_valid(file_path: str, max_duration: int = 300) -> tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, "Файл не существует"
        duration = AudioProcessor.get_audio_duration(file_path)
        if duration == 0:
            return False, "Не удалось определить длительность аудио"
        if duration > max_duration:
            return False, f"Аудио слишком длинное ({duration:.1f} сек). Максимум: {max_duration} сек"
        if duration < 1:
            return False, "Аудио слишком короткое"
        return True, f"Аудио валидно, длительность: {duration:.1f} сек"
