import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8681276775:AAFXzYogHlR-F6BrTTGPqWXHYqa_w6eClp4")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", 1068221701))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- ФУНКЦИИ БОТА ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Здравствуйте, {user.first_name}!\n\n"
        "Это бот для заявок на рекламу у «Хитрого Электрика».\n"
        "Опишите ваше предложение, и я передам его автору."
    )
    await update.message.reply_text(welcome_text)

async def zayavka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Спасибо! Ваша заявка получена. Я свяжусь с вами в ближайшее время."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text
    forward_text = (
        f"📩 Новая заявка!\n"
        f"От: {user.full_name} (@{user.username})\n"
        f"Текст: {user_message}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=forward_text)
    except Exception as e:
        logging.error(f"Не удалось переслать сообщение: {e}")
    await update.message.reply_text("Заявка отправлена автору!")

# --- FLASK ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK"

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('zayavka', zayavka))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
