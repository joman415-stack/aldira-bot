import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن (تم إدخاله مباشرة)
TOKEN = "8763108829:AAFhun12Xpv7xFZcx48bob1ouRucE96_S4k"

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ مرحبًا بك في نظام الدرع العقاري\n"
        "أرسل لي أي استفسار وسأقوم بتحليله."
    )

# استقبال أي رسالة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = f"📊 تم استلام طلبك:\n\n{user_text}\n\n⚙️ جاري تحليل البيانات (نسخة تجريبية)"

    await update.message.reply_text(response)


def main():
    if not TOKEN:
        raise ValueError("TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🛡️ البوت يعمل الآن...")

    app.run_polling()


if __name__ == "__main__":
    main()
