import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Логування
logging.basicConfig(level=logging.INFO)

# Flask застосунок
app = Flask(__name__)

# Будуємо Telegram Application
def build_app():
    return Application.builder().token(os.environ.get("BOT_TOKEN")).build()

tg_app = build_app()

# Клавіатура з кнопкою
MAIN_KB = ReplyKeyboardMarkup(
    [["Попередити охорону"]],
    resize_keyboard=True
)

# Хендлер старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! Натисніть кнопку нижче, щоб попередити охорону.",
        reply_markup=MAIN_KB
    )

# Ловимо кнопку
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Попередити охорону":
        chat_id = os.environ.get("SECURITY_CHAT_ID")
        await tg_app.bot.send_message(
            chat_id,
            f"🚨 Хтось викликає охорону!\nВід: {update.message.from_user.full_name}"
        )
        await update.message.reply_text("Охорону попереджено!")

# Додаємо хендлери
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))


# ========= Flask WEBHOOK =========

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route(f"/{os.environ.get('BOT_TOKEN')}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg_app.bot)
    tg_app.process_update(update)
    return "OK"


# ========= Запуск бота + Flask =========

if __name__ == "__main__":
    import threading
    threading.Thread(target=tg_app.run_polling, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
