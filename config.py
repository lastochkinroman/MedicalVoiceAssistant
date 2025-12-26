import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    SALUTE_SPEECH_TOKEN = os.getenv('SALUTE_SPEECH_TOKEN')
    FFMPEG_PATH = os.getenv('FFMPEG_PATH')
    SALUTE_SPEECH_URL = "https://smartspeech.sber.ru/rest/v1/speech:recognize"
    GROQ_MODEL = "llama3-70b-8192"
    GROQ_TEMPERATURE = 0.7
    TEMP_DIR = "temp_audio"
    MAX_SUMMARY_LENGTH = 1500
