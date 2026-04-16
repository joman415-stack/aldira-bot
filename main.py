import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ==================== الإعدادات ====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔥 التوكن داخل الكود كما طلبت
TOKEN = "8763108829:AAGSyWX_sspwTZMM5G_E8y1QvyDLhZkV_9Q"

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

# ==================== محرك التحليل ====================

def calculate_risk(text):
    score = 50
    reasons = []

    keywords = {
        "بصيرة": 15,
        "وريث": 25,
        "نزاع": 30,
        "خارج المخطط": 15,
        "بدون شهود": 15,
        "بدون أوراق": 20,
        "بيع سريع": 10,
        "وسيط": 10,
        "استثمار": 5,
        "ملكية": -25,
        "عقد": -10,
        "مخطط": 0,
        "سكن": 0
    }

    for word, weight in keywords.items():
        if word in text:
            score += weight
            reasons.append(f"• الكلمة '{word}' أثرت على التقييم ({weight})")

    if score >= 75:
        level = "🚨 مرتفع جداً (خطر)"
        recommendation = "⚠️ ننصح بعدم الإتمام دون فحص قانوني شامل"
    elif score >= 45:
        level = "⚠️ متوسط (تحتاج حذر)"
        recommendation = "📋 يوصى بالفحص الميداني والتأكد من الأوراق"
    else:
        level = "✅ منخفض (آمن نسبياً)"
        recommendation = "👍 يمكن المتابعة مع الاحتياطات المعتادة"

    return score, level, reasons, recommendation

# ==================== الرد على الرسائل ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *مرحباً بك في نظام الدرع العقاري*\n"
        "أرسل أي وصف للعقار وسأقوم بتحليل المخاطر فوراً.",
        parse_mode="Markdown"
    )

async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    score, level, reasons, recommendation = calculate_risk(text)

    report = (
        f"🛡️ *تقرير الدرع العقاري*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 *مؤشر المخاطر:* {score}/100\n"
        f"⚖️ *التصنيف:* {level}\n\n"
        f"📌 *ملاحظات التحليل:*\n"
    )

    if reasons:
        for r in reasons[:5]:
            report += f"{r}\n"
    else:
        report += "• لا توجد ملاحظات خطيرة\n"

    report += (
        f"\n💡 *التوصية:* {recommendation}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔍 *خدمات الفحص الميداني (بريميوم):*\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
        [InlineKeyboardButton("💬 تليجرام", url=CONTACT_TELEGRAM)],
        [InlineKeyboardButton("🌐 الموقع الرسمي", url=WEBSITE_URL)],
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="new")]
    ])

    await update.message.reply_text(report, reply_markup=keyboard, parse_mode="Markdown")

async def new_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✍️ أرسل وصف العقار لتحليل جديد.")

# ==================== التشغيل ====================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))

    app.run_polling()

if __name__ == "__main__":
    main()
