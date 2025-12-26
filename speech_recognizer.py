import os
import uuid
import requests
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self):
        self.api_url = Config.SALUTE_SPEECH_URL
        self.token = Config.SALUTE_SPEECH_TOKEN

    async def recognize_speech(self, audio_file_path: str) -> Optional[str]:
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return None
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            file_size_mb = len(audio_data) / (1024 * 1024)
            if file_size_mb > 10:
                logger.error(f"Audio file too large: {file_size_mb:.2f} MB")
                return None
            headers = {
                'Content-Type': 'audio/x-pcm;bit=16;rate=16000',
                'Authorization': f'Bearer {self.token}',
                'X-Request-ID': str(uuid.uuid4()),
                'Accept': 'application/json'
            }
            logger.info("Sending request to SaluteSpeech API...")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=audio_data,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            if 'result' in result:
                text = result['result'].strip()
                logger.info(f"Speech recognized: {len(text)} characters")
                return text
            else:
                logger.error(f"No 'result' field in response: {result}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in speech recognition: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}")
            return None

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = ' '.join(text.split())
        corrections = {
            'к примеру': 'например',
            'спасибо большое': 'спасибо',
            'пожалуйста большое': 'пожалуйста'
        }
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        return text
