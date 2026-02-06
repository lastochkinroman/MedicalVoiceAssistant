"""Main module for the Medical Voice Assistant Telegram Bot."""

import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)
from telegram.constants import ParseMode

from config import Config
from audio_processor import AudioProcessor
from speech_recognizer import SpeechRecognizer
from medical_analyzer import medical_analyzer

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

# Initialize components
audio_processor = AudioProcessor()
speech_recognizer = SpeechRecognizer()

# Create temporary directory
Path(Config.TEMP_DIR).mkdir(exist_ok=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message."""
    welcome_text = """
🩺 **Medical Assistant Voice Assistant**

Я помогу вам анализировать голосовые обращения пациентов.

**Как это работает:**
1. Пациент отправляет голосовое сообщение с жалобой/вопросом
2. Я распознаю речь через SaluteSpeech
3. Анализирую обращение через Groq AI
4. Предоставляю структурированный анализ

**Что я анализирую:**
• Тип обращения (симптомы, диагностика, лечение и т.д.)
• Основную проблему со здоровьем
• Медицинские детали
• Рекомендации для врача
• Дальнейшие шаги

**Отправьте голосовое сообщение или аудиофайл для анализа.**
    """.strip()

    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show usage instructions."""
    help_text = """
📋 **Инструкция по использованию:**

**Поддерживаемые форматы:**
• Голосовые сообщения Telegram
• Аудио файлы (OGG, MP3, WAV)
• Максимальная длительность: 5 минут

**Процесс обработки:**
1. Загрузка и конвертация аудио
2. Распознавание речи (SaluteSpeech)
3. Медицинский анализ (Groq AI)
4. Формирование отчета

**Качество распознавания зависит от:**
- Четкости речи
- Отсутствия фонового шума
- Качества записи

**Примеры обращений для анализа:**
• "У меня болит голова уже неделю"
• "Проблема с давлением после еды"
• "Как лечить простуду?"
• "Жалоба на аллергию после приема лекарства"

**Команды:**
/start - Начало работы
/help - Эта инструкция
/status - Статус сервисов
    """.strip()

    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - check API status."""
    status_text = "🔍 **Проверка статуса сервисов...**\n\n"
    checks = []

    if Config.TELEGRAM_TOKEN:
        checks.append("✅ Telegram Bot Token")
    else:
        checks.append("❌ Telegram Bot Token")

    if Config.GROQ_API_KEY:
        checks.append("✅ Groq API Key")
    else:
        checks.append("❌ Groq API Key")

    if Config.SALUTE_SPEECH_TOKEN:
        checks.append("✅ SaluteSpeech Token")
    else:
        checks.append("❌ SaluteSpeech Token")

    status_text += "\n".join(checks)
    status_text += "\n\nВсе сервисы готовы к работе! ✅"

    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)


async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming audio messages (voice or audio files)."""
    user = update.effective_user
    message = update.message

    await message.reply_text("🔊 Обрабатываю аудио обращение...")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_id = f"{user.id}_{timestamp}"
        original_file = os.path.join(Config.TEMP_DIR, f"{audio_id}_original")
        wav_file = os.path.join(Config.TEMP_DIR, f"{audio_id}.wav")

        # Determine file type and get file info
        if message.voice:
            file_info = await message.voice.get_file()
            file_ext = ".ogg"
        elif message.audio:
            file_info = await message.audio.get_file()
            file_ext = (
                message.audio.file_name.split(".")[-1]
                if message.audio.file_name else ".mp3"
            )
            file_ext = f".{file_ext.lower()}"
        else:
            await message.reply_text("❌ Не удалось получить аудио файл.")
            return

        original_file += file_ext

        # Download audio
        await message.reply_text("📥 Загружаю аудио...")
        if not await audio_processor.download_telegram_audio(
            file_info.file_path,
            Config.TELEGRAM_TOKEN,
            original_file
        ):
            await message.reply_text("❌ Ошибка при загрузке аудио.")
            return

        # Validate audio
        is_valid, validation_message = audio_processor.is_audio_valid(
            original_file,
            Config.MAX_AUDIO_DURATION
        )
        if not is_valid:
            await message.reply_text(f"❌ {validation_message}")
            await cleanup_files([original_file])
            return

        await message.reply_text(f"✅ {validation_message}")

        # Convert audio
        await message.reply_text("🔄 Конвертирую аудио...")
        if not await audio_processor.convert_to_speech_format(
            original_file, wav_file
        ):
            await message.reply_text("❌ Ошибка при конвертации аудио.")
            await cleanup_files([original_file])
            return

        # Recognize speech
        await message.reply_text("🔍 Распознаю речь...")
        recognized_text = await speech_recognizer.recognize_speech(wav_file)
        if not recognized_text:
            await message.reply_text(
                "❌ Не удалось распознать речь. Попробуйте запись получше."
            )
            await cleanup_files([original_file, wav_file])
            return

        # Clean and analyze text
        cleaned_text = speech_recognizer.clean_text(recognized_text)
        logger.info(
            f"Recognized text for user {user.id}: {cleaned_text[:200]}..."
        )

        await message.reply_text("🤖 Анализирую обращение пациента...")
        analysis_result = await medical_analyzer.analyze_patient_request(
            cleaned_text
        )

        await send_analysis_results(update, analysis_result)
        await cleanup_files([original_file, wav_file])

    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        await message.reply_text(
            "⚠️ Произошла ошибка при обработке. Попробуйте ещё раз."
        )


async def send_analysis_results(update: Update, analysis_result: dict):
    """Send analysis results to user."""
    try:
        response_text = (
            f"📋 **АНАЛИЗ ОБРАЩЕНИЯ ПАЦИЕНТА**\n\n"
            f"{analysis_result['analysis']}\n\n"
            f"🔍 **Ключевые слова:** {', '.join(analysis_result['keywords'])}\n"
            f"📊 **Тип обращения:** {analysis_result['request_type']}\n\n"
            f"🎤 **Распознанный текст (фрагмент):**\n"
            f"_{analysis_result['original_text']}_"
        )

        max_length = 4000
        if len(response_text) > max_length:
            parts = [
                response_text[i:i + max_length]
                for i in range(0, len(response_text), max_length)
            ]
            for i, part in enumerate(parts):
                await update.message.reply_text(
                    part,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                if i < len(parts) - 1:
                    await asyncio.sleep(0.5)
        else:
            await update.message.reply_text(
                response_text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

        await update.message.reply_text("─" * 30)

        follow_up_text = """
💡 **Дальнейшие действия:**
1. Свяжитесь с пациентом для уточнения деталей
2. Назначьте необходимые обследования
3. Рекомендуйте подходящие препараты
4. Запланируйте следующий прием

Хотите проанализировать ещё одно обращение? Просто отправьте голосовое сообщение!
        """.strip()

        await update.message.reply_text(
            follow_up_text,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"Error sending analysis results: {e}")
        await update.message.reply_text("✅ Анализ завершен!")


async def cleanup_files(file_paths):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Error removing file {file_path}: {e}")


def main():
    """Main function to start the bot."""
    # Validate configuration
    missing_vars = Config.validate()
    if missing_vars:
        logger.error(
            "❌ Отсутствуют переменные окружения: %s",
            ", ".join(missing_vars)
        )
        return

    logger.info("Configuration is valid")

    # Initialize Telegram application
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO,
        handle_audio_message
    ))

    logger.info("🤖 Medical Assistant Voice Assistant запущен...")
    logger.info("Ожидание голосовых обращений...")

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()