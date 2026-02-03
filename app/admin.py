from keyboards import admin_menu, main_menu

def register_admin_handlers(bot, ADMIN_ID_ref, SCRIPT_ENABLED_ref, users, all_users):

    def is_admin(uid):
        try:
            return int(uid) == int(ADMIN_ID_ref())
        except:
            return False

    # =====================
    # ОБЩИЙ ВЫВОД АДМИНКИ
    # =====================

    def show_admin_panel(chat_id):
        bot.send_message(
            chat_id,
            "🛠 *Админ-панель*\n\n"
            "/stats — статистика\n"
            "/script_on — включить скрипт\n"
            "/script_off — выключить скрипт\n"
            "/script_status — статус",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

    # =====================
    # /admin
    # =====================

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):
        if not is_admin(message.from_user.id):
            return
        show_admin_panel(message.chat.id)

    # =====================
    # /stats
    # =====================

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
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

    # =====================
    # /script_on
    # =====================

    @bot.message_handler(commands=["script_on"])
    def script_on(message):
        if not is_admin(message.from_user.id):
            return

        SCRIPT_ENABLED_ref(True)
        bot.send_message(
            message.chat.id,
            "🤖 Скрипт *включён*",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

    # =====================
    # /script_off
    # =====================

    @bot.message_handler(commands=["script_off"])
    def script_off(message):
        if not is_admin(message.from_user.id):
            return

        SCRIPT_ENABLED_ref(False)
        bot.send_message(
            message.chat.id,
            "🤖 Скрипт *выключен*",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

    # =====================
    # /script_status
    # =====================

    @bot.message_handler(commands=["script_status"])
    def script_status(message):
        if not is_admin(message.from_user.id):
            return

        bot.send_message(
            message.chat.id,
            f"🤖 Скрипт сейчас: *{'ВКЛЮЧЕН' if SCRIPT_ENABLED_ref() else 'ВЫКЛЮЧЕН'}*",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

    # =====================
    # НАЗАД
    # =====================

    @bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
    def admin_back(message):
        if not is_admin(message.from_user.id):
            return

        bot.send_message(
            message.chat.id,
            "Выход из админ-панели",
            reply_markup=main_menu()
        )
