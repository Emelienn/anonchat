# admin.py
from telebot import TeleBot

def register_admin_handlers(bot: TeleBot, ADMIN_ID_ref, SCRIPT_ENABLED_ref, users, all_users):
    # ADMIN_ID_ref и SCRIPT_ENABLED_ref — ссылки на переменные из основного файла

    def is_admin(uid):
        try:
            return int(uid) == int(ADMIN_ID_ref())
        except:
            return False

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):
        if not is_admin(message.from_user.id):
            return
        bot.send_message(
            message.chat.id,
            "🛠 Админ-панель\n\n"
            "/stats — статистика\n"
            "/script_on — включить скрипт\n"
            "/script_off — выключить скрипт\n"
            "/script_status — статус"
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
            f"🤖 Скрипт: {'ВКЛЮЧЕН' if SCRIPT_ENABLED_ref() else 'ВЫКЛЮЧЕН'}",
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["script_on"])
    def script_on(message):
        if is_admin(message.from_user.id):
            SCRIPT_ENABLED_ref(True)
            bot.send_message(message.chat.id, "🤖 Скрипт *включён*", parse_mode="Markdown")

    @bot.message_handler(commands=["script_off"])
    def script_off(message):
        if is_admin(message.from_user.id):
            SCRIPT_ENABLED_ref(False)
            bot.send_message(message.chat.id, "🤖 Скрипт *выключен*", parse_mode="Markdown")

    @bot.message_handler(commands=["script_status"])
    def script_status(message):
        if is_admin(message.from_user.id):
            bot.send_message(
                message.chat.id,
                f"🤖 Скрипт сейчас: *{'ВКЛЮЧЕН' if SCRIPT_ENABLED_ref() else 'ВЫКЛЮЧЕН'}*",
                parse_mode="Markdown"
            )
