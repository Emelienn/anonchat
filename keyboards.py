# keyboards.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🚀 Начать диалог"))
    return kb

def search_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("⛔ Остановить поиск"))
    return kb

def chat_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("🔄 Следующий собеседник"),
        KeyboardButton("🚪 Выйти из чата")
    )
    return kb
