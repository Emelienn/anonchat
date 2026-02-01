import os
import time
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# =====================
# НАСТРОЙКИ
# =====================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
WELCOME_IMAGE = "welcome.jpg"  # 640x360

# =====================
# СОСТОЯНИЯ
# =====================

users = {}          # user_id -> {state, partner_id}
waiting_list = []   # очередь ожидания
reports = {}        # user_id -> count

# =====================
# КЛАВИАТУРЫ
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
        KeyboardButton("⚠️ Пожаловаться"),
        KeyboardButton("🚪 Выйти из чата")
    )
    return kb

# =====================
# ВСПОМОГАТЕЛЬНОЕ
# =====================

def reset_user(user_id):
    users[user_id] = {
        "state": "none",
        "partner_id": None
    }

def send_welcome(chat_id):
    text = (
        "🖤 *Анонимный чат | 18+*\n\n"
        "Ты полностью анонимен.\n"
        "Без имён. Без истории.\n"
        "Только диалог 1 на 1.\n\n"
        "Нажми кнопку ниже, чтобы начать 💎"
    )

    try:
        with open(WELCOME_IMAGE, "rb") as photo:
            bot.send_photo(
                chat_id,
                photo,
                caption=text,
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
    except:
        bot.send_message(
            chat_id,
            text,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

# =====================
# /START — ВСЕГДА РАБОТАЕТ
# =====================

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    reset_user(user_id)
    send_welcome(user_id)

# =====================
# ПОИСК СОБЕСЕДНИКА
# =====================

def try_find_pair():
    while len(waiting_list) >= 2:
        u1 = waiting_list.pop(0)
        u2 = waiting_list.pop(0)

        if users.get(u1, {}).get("state") != "waiting":
            continue
        if users.get(u2, {}).get("state") != "waiting":
            continue

        users[u1]["state"] = "chatting"
        users[u2]["state"] = "chatting"
        users[u1]["partner_id"] = u2
        users[u2]["partner_id"] = u1

        bot.send_message(u1, "💬 Собеседник найден.\nМожно начинать 👀", reply_markup=chat_menu())
        bot.send_message(u2, "💬 Собеседник найден.\nМожно начинать 👀", reply_markup=chat_menu())

# =====================
# КНОПКИ
# =====================

@bot.message_handler(func=lambda m: m.text == "🚀 Начать диалог")
def start_dialog(message):
    user_id = message.from_user.id

    if user_id not in users:
        reset_user(user_id)

    if users[user_id]["state"] != "none":
        bot.send_message(user_id, "⏳ Ты уже в поиске или в чате")
        return

    users[user_id]["state"] = "waiting"
    waiting_list.append(user_id)

    bot.send_message(
        user_id,
        "⏳ Ищем собеседника…",
        reply_markup=search_menu()
    )
    try_find_pair()


@bot.message_handler(func=lambda m: m.text == "⛔ Остановить поиск")
def stop_search(message):
    user_id = message.from_user.id

    if user_id not in users or users[user_id]["state"] != "waiting":
        return

    if user_id in waiting_list:
        waiting_list.remove(user_id)

    reset_user(user_id)
    send_welcome(user_id)


@bot.message_handler(func=lambda m: m.text == "🔄 Следующий собеседник")
def next_partner(message):
    user_id = message.from_user.id

    if user_id not in users or users[user_id]["state"] != "chatting":
        return

    partner_id = users[user_id]["partner_id"]

    reset_user(user_id)

    if partner_id in users:
        reset_user(partner_id)
        bot.send_message(
            partner_id,
            "❌ Собеседник переключился",
            reply_markup=main_menu()
        )

    users[user_id]["state"] = "waiting"
    waiting_list.append(user_id)

    bot.send_message(
        user_id,
        "🔄 Ищем нового собеседника…",
        reply_markup=search_menu()
    )
    try_find_pair()


@bot.message_handler(func=lambda m: m.text == "🚪 Выйти из чата")
def leave_chat(message):
    user_id = message.from_user.id

    if user_id not in users:
        reset_user(user_id)
        send_welcome(user_id)
        return

    if users[user_id]["state"] == "waiting":
        if user_id in waiting_list:
            waiting_list.remove(user_id)
        reset_user(user_id)
        send_welcome(user_id)
        return

    if users[user_id]["state"] == "chatting":
        partner_id = users[user_id]["partner_id"]
        reset_user(user_id)
        send_welcome(user_id)

        if partner_id in users:
            reset_user(partner_id)
            bot.send_message(
                partner_id,
                "❌ Собеседник покинул чат",
                reply_markup=main_menu()
            )


@bot.message_handler(func=lambda m: m.text == "⚠️ Пожаловаться")
def report_user(message):
    user_id = message.from_user.id

    if user_id not in users or users[user_id]["state"] != "chatting":
        return

    partner_id = users[user_id]["partner_id"]
    reports[partner_id] = reports.get(partner_id, 0) + 1

    bot.send_message(user_id, "✅ Жалоба отправлена")
    leave_chat(message)

# =====================
# СООБЩЕНИЯ В ЧАТЕ
# =====================

@bot.message_handler(content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'
])
def handle_messages(message):
    user_id = message.from_user.id

    if user_id not in users or users[user_id]["state"] != "chatting":
        return

    partner_id = users[user_id]["partner_id"]

    try:
        if message.content_type == "text":
            bot.send_message(partner_id, message.text)
        else:
            getattr(bot, f"send_{message.content_type}")(
                partner_id,
                getattr(message, message.content_type).file_id
            )
    except:
        leave_chat(message)

# =====================
# FALLBACK
# =====================

@bot.message_handler(content_types=['text'])
def safe_fallback(message):
    user_id = message.from_user.id

    if user_id not in users:
        reset_user(user_id)
        send_welcome(user_id)
        return

    if users[user_id]["state"] == "none":
        bot.send_message(
            user_id,
            "Нажми кнопку ниже, чтобы начать 💎",
            reply_markup=main_menu()
        )

# =====================
# СТАРТ
# =====================

if __name__ == "__main__":
    print("🕶 Анонимный чат | 18+ запущен")
    bot.infinity_polling()
