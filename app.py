import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

app = Flask(name)

# Telegram application (створюємо, але не запускаємо polling)
def build_app():
    return Application.builder().token(os.getenv("BOT_TOKEN")).build()

tg = build_app()

# Клавіатура з 1 кнопкою
MAIN_KBD = ReplyKeyboardMarkup(
    [["Попередити охорону"]],
    resize_keyboard=True
)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! Натисніть кнопку нижче, щоб залишити заявку.",
        reply_markup=MAIN_KBD
    )

# Натиснув кнопку
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напишіть кого пропустити і приблизний час.\n\nПриклад: \"Іван, 18:30, авто АА1234ВК\"",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data["waiting_guest"] = True

# Коли користувач пише текст після кнопки
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Якщо очікуємо заявку
    if context.user_data.get("waiting_guest"):
        msg = update.message.text.strip()

        send_to = os.getenv("SECURITY_CHAT_ID")
        await context.bot.send_message(
            chat_id=int(send_to),
            text=f"🔔 НОВА ЗАЯВКА НА ПРОПУСК:\n{msg}"
        )

        context.user_data["waiting_guest"] = False

        await update.message.reply_text(
            "Заявку передано охороні ✔️",
            reply_markup=MAIN_KBD
        )
    else:
        await update.message.reply_text(
            "Натисніть кнопку «Попередити охорону».",
            reply_markup=MAIN_KBD
        )

# РЕЄСТРУЄМО команди
tg.add_handler(CommandHandler("start", start))
tg.add_handler(MessageHandler(filters.Regex("Попередити охорону"), warn))
tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Вебхук маршрут
@app.post("/webhook")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg.bot)
    await tg.process_update(update)
    return "ok", 200

# Головна сторінка (для перевірки)
@app.get("/")
def home():
    return "Bot is running", 200
