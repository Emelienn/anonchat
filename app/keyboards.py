from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# =====================
# ОСНОВНЫЕ КЛАВИАТУРЫ
# =====================

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
    kb.add(KeyboardButton("⚠️ Пожаловаться"))
    return kb

# =====================
# АДМИН-КЛАВИАТУРА
# =====================

def admin_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("Статистика"),
        KeyboardButton("Статус скрипта")
    )
    kb.add(
        KeyboardButton("Вкючить"),
        KeyboardButton("Выключить")
    )
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb
