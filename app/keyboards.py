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
    return kb

# =====================
# АДМИН-КЛАВИАТУРЫ
# =====================

def admin_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("/stats"),
        KeyboardButton("/script_status")
    )
    kb.add(
        KeyboardButton("/script_on"),
        KeyboardButton("/script_off")
    )
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb
