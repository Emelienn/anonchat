import os
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

users = {}
waiting_list = []
reports = {}

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
    users[user_id] = {"state": "none", "partner_id": None}


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
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())

# =====================
# /START
# =====================

@bot.message_handler(commands=["start"])
def start_cmd(message):
    reset_user(message.from_user.id)
    send_welcome(message.from_user.id)

# =====================
# ПОИСК
# =====================

def try_find_pair():
    while len(waiting_list) >= 2:
        u1 = waiting_list.pop(0)
        u2 = waiting_list.pop(0)

        if users.get(u1, {}).get("state") != "waiting":
            continue
        if users.get(u2, {}).get("state") != "waiting":
            continue

        users[u1]["state"] = users[u2]["state"] = "chatting"
        users[u1]["partner_id"] = u2
        users[u2]["partner_id"] = u1

        bot.send_message(u1, "💬 Собеседник найден", reply_markup=chat_menu())
        bot.send_message(u2, "💬 Собеседник найден", reply_markup=chat_menu())

# =====================
# КНОПКИ
# =====================

@bot.message_handler(func=lambda m: m.text == "🚀 Начать диалог")
def start_dialog(message):
    uid = message.from_user.id
    users.setdefault(uid, {"state": "none", "partner_id": None})

    if users[uid]["state"] != "none":
        return

    users[uid]["state"] = "waiting"
    waiting_list.append(uid)
    bot.send_message(uid, "⏳ Ищем собеседника…", reply_markup=search_menu())
    try_find_pair()


@bot.message_handler(func=lambda m: m.text == "⛔ Остановить поиск")
def stop_search(message):
    uid = message.from_user.id
    if users.get(uid, {}).get("state") == "waiting":
        if uid in waiting_list:
            waiting_list.remove(uid)
        reset_user(uid)
        send_welcome(uid)


@bot.message_handler(func=lambda m: m.text == "🔄 Следующий собеседник")
def next_partner(message):
    uid = message.from_user.id
    if users.get(uid, {}).get("state") != "chatting":
        return

    pid = users[uid]["partner_id"]
    reset_user(uid)

    if pid in users:
        reset_user(pid)
        bot.send_message(pid, "❌ Собеседник переключился", reply_markup=main_menu())

    users[uid]["state"] = "waiting"
    waiting_list.append(uid)
    bot.send_message(uid, "🔄 Ищем нового собеседника…", reply_markup=search_menu())
    try_find_pair()


@bot.message_handler(func=lambda m: m.text == "🚪 Выйти из чата")
def leave_chat(message):
    uid = message.from_user.id
    pid = users.get(uid, {}).get("partner_id")

    reset_user(uid)
    send_welcome(uid)

    if pid in users and users[pid]["state"] == "chatting":
        reset_user(pid)
        bot.send_message(pid, "❌ Собеседник покинул чат", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == "⚠️ Пожаловаться")
def report_user(message):
    uid = message.from_user.id
    if users.get(uid, {}).get("state") != "chatting":
        return

    pid = users[uid]["partner_id"]
    reports[pid] = reports.get(pid, 0) + 1
    bot.send_message(uid, "✅ Жалоба отправлена")
    leave_chat(message)

# =====================
# ПЕРЕСЫЛКА ВСЕГО
# =====================

@bot.message_handler(content_types=[
    "text", "photo", "video", "video_note", "voice",
    "audio", "document", "sticker", "animation",
    "location", "contact"
])
def relay(message):
    uid = message.from_user.id
    if users.get(uid, {}).get("state") != "chatting":
        return

    pid = users[uid]["partner_id"]

    try:
        if message.content_type == "text":
            bot.send_message(pid, message.text)
        elif message.content_type == "photo":
            bot.send_photo(pid, message.photo[-1].file_id)
        elif message.content_type == "video":
            bot.send_video(pid, message.video.file_id)
        elif message.content_type == "video_note":
            bot.send_video_note(pid, message.video_note.file_id)
        elif message.content_type == "voice":
            bot.send_voice(pid, message.voice.file_id)
        elif message.content_type == "audio":
            bot.send_audio(pid, message.audio.file_id)
        elif message.content_type == "document":
            bot.send_document(pid, message.document.file_id)
        elif message.content_type == "sticker":
            bot.send_sticker(pid, message.sticker.file_id)
        elif message.content_type == "animation":
            bot.send_animation(pid, message.animation.file_id)
        elif message.content_type == "location":
            bot.send_location(pid, message.location.latitude, message.location.longitude)
        elif message.content_type == "contact":
            bot.send_contact(pid, message.contact.phone_number, message.contact.first_name)
    except Exception as e:
        print("Ошибка пересылки:", e)
        bot.send_message(uid, "⚠️ Сообщение не удалось отправить")

# =====================
# СТАРТ
# =====================

if __name__ == "__main__":
    print("🕶 Анонимный чат | 18+ запущен")
    bot.infinity_polling()
