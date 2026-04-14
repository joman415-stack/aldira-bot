import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ مرحبًا بك في نظام الدرع العقاري\n"
        "أرسل موقع الأرض أو نوع الوثيقة أو أي وصف وسأحلله لك."
    )


async def analyze_real_estate(text: str) -> str:
    if "بصيرة" in text or "عقد" in text or "وثيقة" in text:
        return (
            "📑 تحليل أولي:\n"
            "- تم رصد ذكر وثيقة ملكية\n"
            "- يوصى بالتحقق من قوة السند وسلسلة الملكية\n"
            "- راجع احتمالات النزاع الوراثي أو ازدواج البيع"
        )

    elif "أرض" in text or "قطعة" in text:
        return (
            "🏗️ تحليل استثماري أولي:\n"
            "- تم رصد طلب متعلق بأرض\n"
            "- يلزم التحقق من المخطط والجيران والشارع\n"
            "- مهم مراجعة الاعتراضات المحلية"
        )

    elif "سلام" in text or "هلا" in text:
        return "أهلًا بك 👋 أرسل بيانات العقار أو الوثيقة للبدء."

    else:
        return (
            "📊 تم استلام البيانات\n"
            "⚙️ التحليل المبدئي:\n"
            "- البيانات تحتاج تفاصيل أكثر\n"
            "- أرسل نوع الوثيقة + الموقع + صلة البائع"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    result = await analyze_real_estate(user_text)
    await update.message.reply_text(result)


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🛡️ AL-DIR'A bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
