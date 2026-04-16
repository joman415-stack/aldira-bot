import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, ContextTypes, filters

# ==================== الإعدادات ====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8763108829:AAEp6Hj9vnfm8KBW9xoVfFd5ps3uwYVvYfI"

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

# ==================== لوحة الخيارات ====================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["1) تحليل — استشارة — توجيه"],
        ["2) تعلم الذكاء الاصطناعي والبرومبت"],
        ["3) تصميم — بناء — تطوير"],
        ["4) خدمات أخرى"],
    ],
    resize_keyboard=True
)

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

# ==================== الرسائل ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في منظومة الدرع — يسعدني مساعدتك 🌟\n\n"
        "اختر خدمتك من القائمة:\n"
        "1) تحليل — استشارة — توجيه\n"
        "2) تعلم الذكاء الاصطناعي والبرومبت\n"
        "3) تصميم — بناء — تطوير\n"
        "4) خدمات أخرى\n\n"
        "أو أرسل وصف العقار مباشرة لتحليل المخاطر.",
        reply_markup=MAIN_KEYBOARD
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "منظومة الدرع | لتقييم مخاطر الاستثمار العقاري – اليمن\n\n"
        "مهمتي مساعدتك في:\n"
        "- تحليل العقارات\n"
        "- تقييم المخاطر\n"
        "- تقديم الاستشارات\n"
        "- دعم التعلم والتطوير\n"
        "- توجيهك للقنوات الرسمية\n\n"
        "للتواصل المباشر:\n"
        "واتساب: 778160500"
    )

# ==================== ردود الخيارات ====================

async def handle_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    # خيار 1
    if msg.startswith("1"):
        await update.message.reply_text(
            "شكرًا لاختيارك خدمة التحليل والاستشارة 👇\n\n"
            "أرسل لي الآن:\n"
            "1) نوع العقار\n"
            "2) الموقع\n"
            "3) السعر أو الميزانية\n"
            "4) الهدف\n\n"
            "وسأقوم بتحليل المخاطر وتقديم التوصيات."
        )
        return

    # خيار 2
    if msg.startswith("2"):
        await update.message.reply_text(
            "ممتاز! مسار تعلم الذكاء الاصطناعي متاح بثلاث مستويات 👇\n\n"
            "1) مبتدئ\n"
            "2) متوسط\n"
            "3) محترف\n\n"
            "للمحتوى المتقدم:\n"
            f"{CONTACT_TELEGRAM}"
        )
        return

    # خيار 3
    if msg.startswith("3"):
        await update.message.reply_text(
            "رائع! قبل أن أبدأ في مساعدتك…\n"
            "أرسل لي:\n"
            "1) نوع المشروع\n"
            "2) مثال أو مرجع\n"
            "3) الهدف النهائي\n"
        )
        return

    # خيار 4
    if msg.startswith("4"):
        await update.message.reply_text(
            "يسعدني مساعدتك… ما الخدمة التي تبحث عنها؟\n\n"
            f"واتساب: {CONTACT_PHONE}\n"
            f"القناة: {CONTACT_TELEGRAM}\n"
            f"الموقع: {WEBSITE_URL}"
        )
        return

    # إذا لم يكن خيار → تحليل عقاري
    await analyze_message(update, context)

# ==================== التحليل ====================

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
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(new_analysis))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_options))

    app.run_polling()

if __name__ == "__main__":
    main()
