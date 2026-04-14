import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM"

WHATSAPP = "https://wa.me/967778160500"
TELEGRAM = "https://t.me/fan_al_prompt"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ AL-DIR'A PRO SYSTEM\n\n"
        "أرسل بيانات العقار بالتنسيق التالي:\n"
        "- نوع الوثيقة\n"
        "- الموقع\n"
        "- صفة البائع\n\n"
        "وسأعطيك تقرير مخاطر احترافي."
    )


def risk_engine(text: str):
    t = text.lower()

    score = 50

    # وثائق
    if "بصيرة" in t:
        score += 15
    if "عقد" in t:
        score -= 10
    if "ملكية" in t:
        score -= 20

    # صفة البائع
    if "وريث" in t:
        score += 25
    if "وسيط" in t:
        score += 10
    if "مالك" in t:
        score -= 15

    # موقع (زيادة مخاطرة عامة إذا غير محدد)
    if "صنعاء" in t or "عدن" in t:
        score += 5

    # تحديد المستوى
    if score >= 75:
        level = "🚨 مرتفع"
    elif score >= 45:
        level = "⚠️ متوسط"
    else:
        level = "✅ منخفض"

    return score, level


def build_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 واتساب استشارة", url=WHATSAPP)],
        [InlineKeyboardButton("🎨 قناة فن البرومبت", url=TELEGRAM)]
    ])


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    score, level = risk_engine(text)

    response = f"""🛡️ تقرير AL-DIR'A PRO

📊 درجة المخاطر: {score}/100
⚖️ التصنيف: {level}

📌 التحليل:
- تم تحليل الوثيقة والموقع وصفة البائع
- النتائج مبنية على مؤشرات أولية

"""

    if score >= 75:
        response += "❌ توصية: لا يُنصح بالشراء بدون فحص قانوني عميق"
    elif score >= 45:
        response += "⚠️ توصية: يحتاج تحقق قانوني وميداني"
    else:
        response += "✅ توصية: الوضع جيد نسبيًا لكن راجع التفاصيل"

    await update.message.reply_text(response, reply_markup=build_buttons())


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🛡️ AL-DIR'A PRO 99% RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
