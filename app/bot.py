import os
import telebot
import threading
import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# =====================
# НАСТРОЙКИ
# =====================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN, threaded=True)
WELCOME_IMAGE = "welcome.jpg"

ADMIN_ID = 7358829982

SCRIPT_ENABLED = True
SCRIPT_MESSAGES = [
    "Привет", "привет", "М", "м", "Д?", "Привет м",
    "Хай", "👋🏻", "Мд", "Мд?"
]
SILENT_SKIP_CHANCE = 0.3

# =====================
# СОСТОЯНИЯ
# =====================

users = {}
waiting_list = []
all_users = set()
script_timers = {}

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
        KeyboardButton("🚪 Выйти из чата")
    )
    return kb

# =====================
# ВСПОМОГАТЕЛЬНОЕ
# =====================

def is_admin(uid: int) -> bool:
    return uid == ADMIN_ID

def cancel_script(uid):
    timer = script_timers.pop(uid, None)
    if timer:
        timer.cancel()

def reset_user(uid):
    cancel_script(uid)
    users[uid] = {"state": "none", "partner_id": None}
    all_users.add(uid)
    if uid in waiting_list:
        waiting_list.remove(uid)

def send_welcome(uid):
    text = (
        "🖤 *Анонимный чат | 18+*\n\n"
        "Ты полностью анонимен.\n"
        "Без имён. Без истории.\n\n"
        "Нажми кнопку ниже, чтобы начать 💎"
    )
    try:
        with open(WELCOME_IMAGE, "rb") as photo:
            bot.send_photo(uid, photo, caption=text, parse_mode="Markdown", reply_markup=main_menu())
    except:
        bot.send_message(uid, text, parse_mode="Markdown", reply_markup=main_menu())

# =====================
# АДМИН КОМАНДЫ
# =====================

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "🛠 *Админ-панель*\n\n"
        "/stats — статистика\n"
        "/script_on — включить скрипт\n"
        "/script_off — выключить скрипт\n"
        "/script_status — статус",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["stats"])
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        return

    online = sum(1 for u in users.values() if u["state"] != "none")
    searching = sum(1 for u in users.values() if u["state"] == "waiting")
    chatting = sum(1 for u in users.values() if u["state"] == "chatting")

    bot.send_message(
        message.chat.id,
        "📊 *Статистика бота*\n\n"
        f"👥 Всего пользователей: {len(all_users)}\n"
        f"🟢 Онлайн сейчас: {online}\n"
        f"🔍 В поиске: {searching}\n"
        f"💬 В чате: {chatting}\n\n"
        f"🤖 Скрипт: {'ВКЛЮЧЕН' if SCRIPT_ENABLED else 'ВЫКЛЮЧЕН'}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["script_on"])
def script_on(message):
    global SCRIPT_ENABLED
    if not is_admin(message.from_user.id):
        return
    SCRIPT_ENABLED = True
    bot.send_message(message.chat.id, "🤖 Скрипт *включён*", parse_mode="Markdown")

@bot.message_handler(commands=["script_off"])
def script_off(message):
    global SCRIPT_ENABLED
    if not is_admin(message.from_user.id):
        return
    SCRIPT_ENABLED = False
    bot.send_message(message.chat.id, "🤖 Скрипт *выключен*", parse_mode="Markdown")

@bot.message_handler(commands=["script_status"])
def script_status(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        f"🤖 Скрипт сейчас: *{'ВКЛЮЧЕН' if SCRIPT_ENABLED else 'ВЫКЛЮЧЕН'}*",
        parse_mode="Markdown"
    )

# =====================
# СКРИПТ
# =====================

def run_script(uid):
    if not SCRIPT_ENABLED:
        return
    if users.get(uid, {}).get("state") != "waiting":
        return
    if len(waiting_list) != 1:
        return

    users[uid]["state"] = "script"
    waiting_list.remove(uid)

    bot.send_message(uid, "💬 Собеседник найден", reply_markup=chat_menu())

    def step():
        if users.get(uid, {}).get("state") != "script":
            return

        if random.random() > SILENT_SKIP_CHANCE:
            bot.send_message(uid, random.choice(SCRIPT_MESSAGES))

        def skip():
            if users.get(uid, {}).get("state") == "script":
                reset_user(uid)
                bot.send_message(uid, "❌ Собеседник переключился", reply_markup=main_menu())

        threading.Timer(4, skip).start()

    script_timers[uid] = threading.Timer(2, step)
    script_timers[uid].start()

# =====================
# /START
# =====================

@bot.message_handler(commands=["start"])
def start_cmd(message):
    reset_user(message.from_user.id)
    send_welcome(message.from_user.id)

# =====================
# ПОИСК ПАР
# =====================

def try_find_pair():
    while len(waiting_list) >= 2:
        u1 = waiting_list.pop(0)
        u2 = waiting_list.pop(0)

        if users.get(u1, {}).get("state") != "waiting":
            continue
        if users.get(u2, {}).get("state") != "waiting":
            continue

        cancel_script(u1)
        cancel_script(u2)

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
    all_users.add(uid)

    if users[uid]["state"] != "none":
        return

    users[uid]["state"] = "waiting"
    waiting_list.append(uid)

    bot.send_message(uid, "⏳ Ищем собеседника…", reply_markup=search_menu())
    try_find_pair()

    if SCRIPT_ENABLED and len(waiting_list) == 1:
        run_script(uid)

@bot.message_handler(func=lambda m: m.text in ["⛔ Остановить поиск", "🚪 Выйти из чата"])
def stop_search(message):
    reset_user(message.from_user.id)
    bot.send_message(message.from_user.id, "Поиск остановлен", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔄 Следующий собеседник")
def next_partner(message):
    uid = message.from_user.id
    pid = users.get(uid, {}).get("partner_id")

    reset_user(uid)

    if pid and users.get(pid, {}).get("state") == "chatting":
        reset_user(pid)
        bot.send_message(pid, "❌ Собеседник переключился", reply_markup=main_menu())

    users[uid]["state"] = "waiting"
    waiting_list.append(uid)

    bot.send_message(uid, "🔄 Ищем нового собеседника…", reply_markup=search_menu())
    try_find_pair()

    if SCRIPT_ENABLED and len(waiting_list) == 1:
        run_script(uid)

# =====================
# ПЕРЕСЫЛКА
# =====================

@bot.message_handler(
    content_types=[
        "text", "photo", "video", "video_note", "voice",
        "audio", "document", "sticker", "animation",
        "location", "contact"
    ]
)
def relay(message):
    uid = message.from_user.id
    if users.get(uid, {}).get("state") != "chatting":
        return

    pid = users[uid]["partner_id"]
    if not pid:
        return

    try:
        if message.content_type == "text":
            bot.send_message(pid, message.text)
        else:
            getattr(bot, f"send_{message.content_type}")(
                pid,
                getattr(message, message.content_type).file_id
            )
    except:
        reset_user(uid)
        bot.send_message(uid, "❌ Диалог завершён", reply_markup=main_menu())

# =====================
# СТАРТ
# =====================

if __name__ == "__main__":
    print("🖤 Анонимный чат | 18+ запущен")
    bot.infinity_polling(skip_pending=True)
