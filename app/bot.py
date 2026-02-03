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

bot = telebot.TeleBot(TOKEN)
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

def cancel_script(uid):
    timer = script_timers.pop(uid, None)
    if timer:
        try:
            timer.cancel()
        except Exception:
            pass

def reset_user(uid):
    cancel_script(uid)
    users[uid] = {"state": "none", "partner_id": None}
    all_users.add(uid)
    if uid in waiting_list:
        try:
            waiting_list.remove(uid)
        except ValueError:
            pass

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
    except Exception:
        bot.send_message(uid, text, parse_mode="Markdown", reply_markup=main_menu())

def is_admin(uid):
    return uid == ADMIN_ID

# =====================
# РОУТЕР ДЛЯ АДМИН-КОМАНД (УНИВЕРСАЛЬНЫЙ)
# =====================

ADMIN_CMDS = {"/admin", "/stats", "/script_on", "/script_off", "/script_status"}

@bot.message_handler(func=lambda m: m.text and m.text.split()[0].split("@")[0] in ADMIN_CMDS)
def admin_command_router(message):
    cmd = message.text.split()[0].split("@")[0]
    uid = message.from_user.id
    chat_id = message.chat.id

    # разрешаем админские команды только администратору
    if not is_admin(uid):
        return

    if cmd == "/admin":
        bot.send_message(
            chat_id,
            "🛠 *Админ-панель*\n\n"
            "/stats — статистика\n"
            "/script_on — включить скрипт\n"
            "/script_off — выключить скрипт\n"
            "/script_status — статус",
            parse_mode="Markdown"
        )
        return

    if cmd == "/stats":
        online = sum(1 for u in users.values() if u.get("state") != "none")
        searching = sum(1 for u in users.values() if u.get("state") == "waiting")
        chatting = sum(1 for u in users.values() if u.get("state") == "chatting")

        bot.send_message(
            chat_id,
            "📊 *Статистика бота*\n\n"
            f"👥 Всего пользователей: {len(all_users)}\n"
            f"🟢 Пользовались сейчас: {online}\n"
            f"🔍 В поиске: {searching}\n"
            f"💬 В чате: {chatting}\n\n"
            f"🤖 Скрипт: {'ВКЛЮЧЕН' if SCRIPT_ENABLED else 'ВЫКЛЮЧЕН'}",
            parse_mode="Markdown"
        )
        return

    if cmd == "/script_on":
        global SCRIPT_ENABLED
        SCRIPT_ENABLED = True
        bot.send_message(chat_id, "🤖 Скрипт *включён*", parse_mode="Markdown")
        return

    if cmd == "/script_off":
        SCRIPT_ENABLED = False
        bot.send_message(chat_id, "🤖 Скрипт *выключен*", parse_mode="Markdown")
        return

    if cmd == "/script_status":
        bot.send_message(
            chat_id,
            f"🤖 Скрипт сейчас: *{'ВКЛЮЧЕН' if SCRIPT_ENABLED else 'ВЫКЛЮЧЕН'}*",
            parse_mode="Markdown"
        )
        return

# =====================
# СКРИПТ
# =====================

def run_script(uid):
    if not SCRIPT_ENABLED:
        return
    if uid in script_timers:
        return
    if users.get(uid, {}).get("state") != "waiting":
        return
    if len(waiting_list) != 1:
        return

    users[uid]["state"] = "script"
    if uid in waiting_list:
        try:
            waiting_list.remove(uid)
        except ValueError:
            pass

    try:
        bot.send_message(uid, "💬 Собеседник найден", reply_markup=chat_menu())
    except Exception:
        pass

    def step():
        if users.get(uid, {}).get("state") != "script":
            return

        if random.random() > SILENT_SKIP_CHANCE:
            try:
                bot.send_message(uid, random.choice(SCRIPT_MESSAGES))
            except Exception:
                pass

        def skip():
            if users.get(uid, {}).get("state") == "script":
                reset_user(uid)
                try:
                    bot.send_message(uid, "❌ Собеседник переключился", reply_markup=main_menu())
                except Exception:
                    pass

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
# ПОИСК ПАРЫ
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
    if uid not in waiting_list:
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

    if pid in users and users[pid]["state"] == "chatting":
        reset_user(pid)
        bot.send_message(pid, "❌ Собеседник переключился", reply_markup=main_menu())

    users[uid]["state"] = "waiting"
    waiting_list.append(uid)

    bot.send_message(uid, "🔄 Ищем нового собеседника…", reply_markup=search_menu())
    try_find_pair()

    if SCRIPT_ENABLED and len(waiting_list) == 1:
        run_script(uid)

# =====================
# ПЕРЕСЫЛКА (УНИВЕРСАЛЬНАЯ)
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
        bot.copy_message(pid, message.chat.id, message.message_id)
    except Exception as e:
        print("Relay error:", e)
        reset_user(uid)
        try:
            bot.send_message(uid, "❌ Диалог завершён", reply_markup=main_menu())
        except Exception:
            pass

# =====================
# СТАРТ
# =====================

if __name__ == "__main__":
    print("🖤 Анонимный чат | 18+ запущен")
    bot.infinity_polling()
