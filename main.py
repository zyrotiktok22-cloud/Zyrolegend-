import os
import logging
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters,
)

TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0") or "0")
DB_PATH = os.getenv("DB_PATH", "zyro_bot.db")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("zyro-legend")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY,
        chat_type TEXT,
        language TEXT DEFAULT 'en',
        first_seen TEXT
    )""")
    conn.commit()
    return conn


def save_chat(chat):
    with db() as conn:
        conn.execute(
            """INSERT INTO chats(chat_id, chat_type, first_seen)
               VALUES (?, ?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET chat_type=excluded.chat_type""",
            (chat.id, chat.type, datetime.now(timezone.utc).isoformat()),
        )


def get_lang(chat_id):
    with db() as conn:
        row = conn.execute(
            "SELECT language FROM chats WHERE chat_id=?", (chat_id,)
        ).fetchone()
    return row[0] if row else "en"


def set_lang(chat_id, lang):
    with db() as conn:
        conn.execute(
            """INSERT INTO chats(chat_id, chat_type, language, first_seen)
               VALUES (?, 'private', ?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET language=excluded.language""",
            (chat_id, lang, datetime.now(timezone.utc).isoformat()),
        )


def is_admin(user_id):
    return OWNER_ID != 0 and user_id == OWNER_ID


TEXT = {
    "en": {
        "welcome": "👑 Welcome to *ZYRO LEGEND¹ BOT*!\nChoose an option below.",
        "menu": "🏠 Main menu",
        "admin": "👑 Admin panel",
        "groups": "👥 Group tools",
        "media": "🖼 Media tools",
        "help": "❓ Help",
        "about": "ℹ️ About",
        "language": "🌐 Language",
        "help_text": (
            "Available commands:\n/start — Open menu\n/id — Show chat/user ID\n"
            "/help — Help\n\nGroup admins:\n/welcome_on — Enable welcome messages\n"
            "/welcome_off — Disable welcome messages\n\nOwner:\n/broadcast — Reply to a message with /broadcast"
        ),
        "about_text": "ZYRO LEGEND¹ BOT\nBilingual Telegram assistant: English + Somali.\nHosted with GitHub and Render.",
        "admin_text": "👑 Owner panel\n/broadcast — Reply to a message to broadcast it to saved chats\n/stats — Show saved chat count",
        "groups_text": "👥 Group tools\n/welcome_on — Enable new-member greetings\n/welcome_off — Disable new-member greetings\n/id — Show this chat ID",
        "media_text": "🖼 Send a photo, video, or document to share it in this chat. The bot can also copy a message when the owner uses /broadcast.",
        "choose_lang": "Choose your language:",
        "lang_saved": "✅ Language saved.",
        "not_admin": "⛔ This command is for the bot owner or group administrators.",
        "welcome_new": "👋 Welcome, {name}! Please read the group rules.",
        "broadcast_done": "✅ Broadcast finished. Sent: {sent}, failed: {failed}.",
        "no_reply": "Reply to the message you want to broadcast, then send /broadcast.",
        "stats": "Saved chats: {count}",
    },
    "so": {
        "welcome": "👑 Ku soo dhowow *ZYRO LEGEND¹ BOT*!\nDooro qaybta aad rabto.",
        "menu": "🏠 Liiska hore",
        "admin": "👑 Maamulka bot-ka",
        "groups": "👥 Qalabka group-ka",
        "media": "🖼 Sawirro iyo muuqaallo",
        "help": "❓ Caawimaad",
        "about": "ℹ️ Ku saabsan",
        "language": "🌐 Luqadda",
        "help_text": (
            "Amarrada:\n/start — Fur menu-ga\n/id — Tus ID-ga\n/help — Caawimaad\n\n"
            "Maamulka group-ka:\n/welcome_on — Daar soo dhaweynta\n"
            "/welcome_off — Demi soo dhaweynta\n\n"
            "Owner:\n/broadcast — Reply ku samee fariin kadib qor /broadcast"
        ),
        "about_text": "ZYRO LEGEND¹ BOT\nBot Telegram ah oo ku shaqeeya Somali + English.\nGitHub iyo Render ayaa lagu host-gareeyaa.",
        "admin_text": "👑 Maamulka Owner-ka\n/broadcast — Reply fariin kadib dir\n/stats — Tirada chats-ka kaydsan",
        "groups_text": "👥 Qalabka group-ka\n/welcome_on — Daar soo dhaweynta xubnaha cusub\n/welcome_off — Demi soo dhaweynta\n/id — Tus ID-ga group-ka",
        "media_text": "🖼 Waxaad halkan ku diri kartaa sawir, video ama document. Owner-ku wuxuu fariin u diri karaa chats-ka kaydsan isagoo adeegsanaya /broadcast.",
        "choose_lang": "Dooro luqadda:",
        "lang_saved": "✅ Luqadda waa la beddelay.",
        "not_admin": "⛔ Amarkaan waxaa isticmaali kara maamulka group-ka ama owner-ka bot-ka.",
        "welcome_new": "👋 Soo dhowow {name}! Fadlan akhri xeerarka group-ka.",
        "broadcast_done": "✅ Fariinta waa la diray. Guulaystay: {sent}, fashilmay: {failed}.",
        "no_reply": "Marka hore reply ku samee fariinta aad rabto in la diro, kadib qor /broadcast.",
        "stats": "Chats kaydsan: {count}",
    },
}


def t(chat_id, key):
    return TEXT[get_lang(chat_id)].get(key, TEXT["en"].get(key, key))


def main_keyboard(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(chat_id, "admin"), callback_data="admin"),
         InlineKeyboardButton(t(chat_id, "groups"), callback_data="groups")],
        [InlineKeyboardButton(t(chat_id, "media"), callback_data="media"),
         InlineKeyboardButton(t(chat_id, "help"), callback_data="help")],
        [InlineKeyboardButton(t(chat_id, "about"), callback_data="about"),
         InlineKeyboardButton(t(chat_id, "language"), callback_data="language")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    save_chat(chat)
    banner = Path(__file__).with_name("bot_banner.png")
    if banner.exists():
        with banner.open("rb") as photo:
            await update.effective_message.reply_photo(
                photo=photo,
                caption=t(chat.id, "welcome"),
                reply_markup=main_keyboard(chat.id),
                parse_mode="Markdown",
            )
    else:
        await update.effective_message.reply_text(
            t(chat.id, "welcome"), reply_markup=main_keyboard(chat.id),
            parse_mode="Markdown",
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    save_chat(chat)
    await update.effective_message.reply_text(t(chat.id, "help_text"))


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    save_chat(chat)
    await update.effective_message.reply_text(
        f"Chat ID: `{chat.id}`\nUser ID: `{user.id}`",
        parse_mode="Markdown",
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    save_chat(query.message.chat)
    data = query.data

    if data == "language":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇸🇴 Soomaali", callback_data="lang_so"),
        ]])
        await query.edit_message_text(t(chat_id, "choose_lang"), reply_markup=keyboard)
        return

    if data in ("lang_en", "lang_so"):
        set_lang(chat_id, data[-2:])
        await query.edit_message_text(
            t(chat_id, "lang_saved"), reply_markup=main_keyboard(chat_id)
        )
        return

    if data == "admin":
        if is_admin(query.from_user.id):
            msg = t(chat_id, "admin_text")
        else:
            msg = t(chat_id, "not_admin")
    elif data == "groups":
        msg = t(chat_id, "groups_text")
    elif data == "media":
        msg = t(chat_id, "media_text")
    elif data == "help":
        msg = t(chat_id, "help_text")
    elif data == "about":
        msg = t(chat_id, "about_text")
    else:
        msg = t(chat_id, "menu")

    await query.edit_message_text(msg, reply_markup=main_keyboard(chat_id))


async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private":
        await update.effective_message.reply_text(t(chat.id, "not_admin"))
        return
    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status not in ("administrator", "creator") and not is_admin(user.id):
        await update.effective_message.reply_text(t(chat.id, "not_admin"))
        return
    context.application.bot_data.setdefault("welcome_enabled", {})[chat.id] = (
        update.effective_message.text == "/welcome_on"
    )
    enabled = context.application.bot_data["welcome_enabled"][chat.id]
    lang = get_lang(chat.id)
    answer = ("Welcome messages enabled." if enabled else "Welcome messages disabled.")
    if lang == "so":
        answer = "Soo dhaweynta waa la daaray." if enabled else "Soo dhaweynta waa la damiyey."
    await update.effective_message.reply_text(answer)


async def new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    save_chat(chat)
    enabled = context.application.bot_data.setdefault("welcome_enabled", {}).get(chat.id, True)
    if not enabled:
        return
    for member in update.effective_message.new_chat_members:
        name = member.first_name or "friend"
        await update.effective_message.reply_text(
            t(chat.id, "welcome_new").format(name=name)
        )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text(t(update.effective_chat.id, "not_admin"))
        return
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    await update.effective_message.reply_text(t(update.effective_chat.id, "stats").format(count=count))


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.effective_message.reply_text(t(update.effective_chat.id, "not_admin"))
        return
    source = update.effective_message.reply_to_message
    if not source:
        await update.effective_message.reply_text(t(update.effective_chat.id, "no_reply"))
        return
    with db() as conn:
        chat_ids = [row[0] for row in conn.execute("SELECT chat_id FROM chats").fetchall()]
    sent = failed = 0
    for chat_id in chat_ids:
        try:
            await context.bot.copy_message(
                chat_id=chat_id, from_chat_id=source.chat_id, message_id=source.message_id
            )
            sent += 1
        except Exception as exc:
            log.warning("Broadcast to %s failed: %s", chat_id, exc)
            failed += 1
    await update.effective_message.reply_text(
        t(update.effective_chat.id, "broadcast_done").format(sent=sent, failed=failed)
    )


async def track_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat:
        save_chat(update.effective_chat)


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it in Render Environment Variables.")
    if OWNER_ID == 0:
        log.warning("OWNER_ID is not set. Owner-only commands will be unavailable.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("welcome_on", welcome_toggle))
    app.add_handler(CommandHandler("welcome_off", welcome_toggle))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_members))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, track_chat))
    log.info("ZYRO LEGEND¹ BOT is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
