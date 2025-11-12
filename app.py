import os
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Flask сервер (для Render)
app = Flask(name)

# Телеграм бот
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECURITY_CHAT_ID = os.getenv("SECURITY_CHAT_ID")  # ID групи охорони

application = Application.builder().token(BOT_TOKEN).build()

# Кнопка
MAIN_KB = ReplyKeyboardMarkup(
    [["Попередити охорону"]],
    resize_keyboard=True
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Натисніть кнопку нижче, щоб попередити охорону.",
        reply_markup=MAIN_KB
    )

# Обробка натискання
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Попередити охорону":
        await context.bot.send_message(
            chat_id=SECURITY_CHAT_ID,
            text="🔔 Хтось викликає охорону з бота!"
        )
        await update.message.reply_text("Охорону попереджено!")
    else:
        await update.message.reply_text(
            "Натисніть кнопку нижче.",
            reply_markup=MAIN_KB
        )

# Реєстрація хендлерів
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT, message_handler))

# Render Flask endpoint
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# Запуск бота
if name == "main":
    from threading import Thread

    # Запускаємо Telegram бота окремо
    def run_bot():
        application.run_polling()

    Thread(target=run_bot).start()

    # Запускаємо Flask сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
