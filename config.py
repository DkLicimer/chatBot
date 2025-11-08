# file: config.py
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# --- Токены и ID ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# --- Настройки SMTP для email ---
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# --- Валидация и преобразование ID группы ---
try:
    # Преобразуем строковое значение из .env в число
    admin_group_id = int(GROUP_ID)
except (ValueError, TypeError):
    logging.critical("GROUP_ID не найден или имеет неверный формат в .env!")
    admin_group_id = 0

# --- Регулярные выражения для валидации ---
PHONE_REGEX = r"^\+?[78][-\s(]*\d{3}[-\s)]*\d{3}[-\s]*\d{2}[-\s]*\d{2}$"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"