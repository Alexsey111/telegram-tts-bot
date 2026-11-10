"""Настройки бота. Секреты берутся из окружения, в коде их нет.

Перед запуском задайте переменные:
  TELEGRAM_BOT_TOKEN  токен от @BotFather
  ELEVENLABS_API_KEY  ключ из личного кабинета elevenlabs.io
"""
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_API_URL = os.getenv("ELEVENLABS_API_URL", "https://api.elevenlabs.io/v1")

# Максимальная длина текста для озвучки (символов)
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "5000"))

# Папка для временного хранения аудиофайлов
TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR", "temp_audio")

SUPPORTED_FORMATS = ["mp3", "wav"]
