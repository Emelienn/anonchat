import os
import telebot
import threading
import random
import time

from keyboards import main_menu, search_menu, chat_menu
from admin import register_admin_handlers
from script import run_script

# =====================
# НАСТРОЙКИ
# =====================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)
WELCOME_IMAGE = "welcome.jpg"

ADMIN_ID = 7358829982
SCRIPT_ENABLED = True

def ADMIN_ID_ref():
    return ADMIN_ID

def SCRIPT_ENABLED_ref(value=None):
    global SCRIPT_ENABLED
    if value is None:
        return SCRIPT_ENABLED
    SCRIPT_ENABLED = value

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
# РЕГИСТРАЦИЯ АДМИНКИ
# =====================

register_admin_handlers(
    bot=bot,
    ADMIN_ID_ref=ADMIN_ID_ref,
    SCRIPT_ENABLED_ref=SCRIPT_ENABLED_ref,
    users=users,
    all_users=all_users
)

# =====================
# ВСПОМОГАТЕЛЬНОЕ
# =====================

def cancel_script(uid):
    timer = script_timers.pop(uid, None)
    if timer:
        timer.cancel()

def reset_user(uid):
    users[uid] = {"state": "none", "partner_id": None}
    all_users.add(uid)
    cancel_script(uid)
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
            bot.send_photo(
                uid,
                photo,
                caption=text,
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
    except:
        bot.send_message(
            uid,
            text,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

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
        run_script(
            bot=bot,
            uid=uid,
            users=users,
            waiting_list=waiting_list,
            script_timers=script_timers,
            SCRIPT_ENABLED_ref=SCRIPT_ENABLED_ref,
            SCRIPT_MESSAGES=SCRIPT_MESSAGES,
            SILENT_SKIP_CHANCE=SILENT_SKIP_CHANCE,
            reset_user=reset_user,
            chat_menu=chat_menu,
            main_menu=main_menu
        )

@bot.message_handler(func=lambda m: m.text in ["⛔ Остановить поиск", "🚪 Выйти из чата"])
def stop_search(message):
    reset_user(message.from_user.id)
    bot.send_message(message.from_user.id, "Поиск остановлен", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔄 Следующий собеседник")
def next_partner(message):
    uid = message.from_user.id
    pid = users.get(uid, {}).get("partner_id")

    reset_user(uid)

    if pid in users and users[pid]["state"] == "chatting":
        reset_user(pid)
        bot.send_message(pid, "❌ Собеседник переключился", reply_markup=main_menu())

    users[uid]["state"] = "waiting"
    waiting_list.append(uid)

    bot.send_message(uid, "🔄 Ищем нового собеседника…", reply_markup=search_menu())
    try_find_pair()

    if SCRIPT_ENABLED and len(waiting_list) == 1:
        run_script(
            bot=bot,
            uid=uid,
            users=users,
            waiting_list=waiting_list,
            script_timers=script_timers,
            SCRIPT_ENABLED_ref=SCRIPT_ENABLED_ref,
            SCRIPT_MESSAGES=SCRIPT_MESSAGES,
            SILENT_SKIP_CHANCE=SILENT_SKIP_CHANCE,
            reset_user=reset_user,
            chat_menu=chat_menu,
            main_menu=main_menu
        )

# =====================
# ЖАЛОБА
# =====================

@bot.message_handler(func=lambda m: m.text == "⚠️ Пожаловаться")
def report_user(message):
    uid = message.from_user.id

    if users.get(uid, {}).get("state") != "chatting":
        return

    pid = users[uid].get("partner_id")

    bot.send_message(
        ADMIN_ID,
        f"⚠️ Жалоба\n\n"
        f"От пользователя: {uid}\n"
        f"На пользователя: {pid}"
    )

    if pid in users:
        reset_user(pid)
        bot.send_message(pid, "❌ Диалог завершён", reply_markup=main_menu())

    reset_user(uid)
    bot.send_message(uid, "⚠️ Жалоба отправлена. Диалог завершён.", reply_markup=main_menu())

# =====================
# ПЕРЕСЫЛКА
# =====================

@bot.message_handler(content_types=[
    "text", "photo", "video", "video_note", "voice",
    "audio", "document", "sticker", "animation",
    "location", "contact"
])
def relay(message):
    if message.text and message.text.startswith("/"):
        return

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
    bot.remove_webhook()

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)
