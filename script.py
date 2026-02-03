# script.py
import threading
import random

def run_script(
    *,
    bot,
    uid,
    users,
    waiting_list,
    script_timers,
    SCRIPT_ENABLED_ref,
    SCRIPT_MESSAGES,
    SILENT_SKIP_CHANCE,
    reset_user,
    chat_menu,
    main_menu
):
    if not SCRIPT_ENABLED_ref():
        return
    if users.get(uid, {}).get("state") != "waiting":
        return
    if len(waiting_list) != 1:
        return

    # изолируем пользователя
    users[uid]["state"] = "script"
    if uid in waiting_list:
        waiting_list.remove(uid)

    # уведомление как у реального мэтча
    bot.send_message(uid, "💬 Собеседник найден", reply_markup=chat_menu())

    def step():
        if users.get(uid, {}).get("state") != "script":
            return

        if random.random() > SILENT_SKIP_CHANCE:
            bot.send_message(uid, random.choice(SCRIPT_MESSAGES))

        def skip():
            if users.get(uid, {}).get("state") == "script":
                reset_user(uid)
                bot.send_message(
                    uid,
                    "❌ Собеседник переключился",
                    reply_markup=main_menu()
                )

        threading.Timer(4, skip).start()

    script_timers[uid] = threading.Timer(2, step)
    script_timers[uid].start()
