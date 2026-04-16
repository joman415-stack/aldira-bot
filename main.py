import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمراقبة الأداء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8763108829:AAGSyWX_sspwTZMM5G_E8y1QvyDLhZkV_9"

# البيانات المحدثة
CONTACT_PHONE = "96777160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://sites.google.com/view/aldira-yemen"

# القائمة الرئيسية
MAIN_MENU = [
    ["1) تحليل — استشارة — توجيه"],
    ["2) تعلم الذكاء الاصطناعي والبرومبت"],
    ["3) تصميم — بناء — تطوير"],
    ["4) خدمات أخرى"]
]

# دالة تحليل المخاطر العقارية
def analyze_real_estate(text):
    score = 50
    risk_keywords = ["بصيرة", "وريث", "نزاع", "بدون ورق", "بيع سريع", "خارج المخطط"]
    safe_keywords = ["عقد", "ملكية", "توثيق", "سجل عقاري", "محكمة"]

    for word in risk_keywords:
        if word in text:
            score += 15
    for word in safe_keywords:
        if word in text:
            score -= 10

    score = max(0, min(100, score))
    
    if score >= 70:
        return score, "🚨 خطر مرتفع", "⚠️ لا تقم بدفع أي مبالغ! العقار يحتاج فحصاً قانونياً دقيقاً."
    elif score >= 40:
        return score, "⚠️ خطر متوسط", "📋 تأكد من مطابقة الأوراق ميدانياً ومن حضور جميع الورثة."
    else:
        return score, "✅ خطر منخفض", "👍 العقار يبدو قانونياً، اتبع الإجراءات الرسمية المعتادة."

# دالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"مرحباً بك يا {user_name} في منظومة الدرع 🛡️\n\n"
        "أنا مساعدك الذكي لتقييم المخاطر العقارية والخدمات التقنية.\n"
        "اختر من القائمة أدناه أو أرسل وصف العقار لتحليله:",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    )

# دالة معالجة النصوص
async def handle_text_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "1)" in text:
        await update.message.reply_text("ارسل الآن وصفاً للعقار (المنطقة، نوع الوثائق، الحالة القانونية) وسأقوم بتحليله فوراً.")
    elif "2)" in text:
        await update.message.reply_text(f"لمسارات تعلم الذكاء الاصطناعي وهندسة الأوامر، تابعنا هنا:\n{CONTACT_TELEGRAM}")
    elif "3)" in text:
        await update.message.reply_text(f"نحن هنا لمساعدتك في بناء مشروعك التقني. يمكنك الاطلاع على أعمالنا عبر الرابط:\n{WEBSITE_URL}")
    elif "4)" in text:
        await update.message.reply_text(f"للتواصل المباشر والاستشارات الخاصة:\nواتساب: {CONTACT_PHONE}\nتليجرام: {CONTACT_TELEGRAM}")
    else:
        score, level, recommendation = analyze_real_estate(text)
        report = (
            f"🛡️ *تقرير الدرع العقاري*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 مؤشر المخاطر: {score}/100\n"
            f"⚖️ التقييم الفني: {level}\n\n"
            f"💡 التوصية: {recommendation}"
        )
        await update.message.reply_text(report, parse_mode="Markdown")

# التشغيل الأساسي
def main():
    try:
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_logic))

        print("✅ منظومة الدرع تعمل الآن...")
        application.run_polling(drop_pending_updates=True)

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    main()
