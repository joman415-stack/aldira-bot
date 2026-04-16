import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ⚠️ هام: لا تضع التوكن داخل الكود أبداً!
# استخدم متغير بيئة بدلاً من ذلك
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8763108829:AAGyU_7wTKMLGHz8_EYoUbudQ0ITYGXYNDI")

# 2. لوحة التحكم الرئيسية
MAIN_MENU = [
    ["📊 1) تحليل — استشارة — توجيه"],
    ["🤖 2) تعلم الذكاء الاصطناعي والبرومبت"],
    ["🛠️ 3) تصميم — بناء — تطوير"],
    ["🔧 4) خدمات أخرى"]
]

# 3. تحسين منطق تحليل المخاطر
RISK_KEYWORDS = {
    "بصيرة": 15, "وريث": 25, "نزاع": 30, "بدون ورق": 25,
    "بيع سريع": 15, "قضية": 35, "محكمة": 40, "حجز": 30
}
SAFE_KEYWORDS = {
    "عقد": -10, "ملكية": -15, "توثيق": -15, "مخطط": -5,
    "سند": -10, "رسمي": -12, "مسجل": -8
}

def analyze_real_estate(text: str):
    text_lower = text.lower()
    score = 50
    reasons = []
    
    for word, weight in RISK_KEYWORDS.items():
        if word in text_lower:
            score += weight
            reasons.append(f"⚠️ كلمة '{word}' تزيد المخاطر بنسبة {weight}%")
    
    for word, weight in SAFE_KEYWORDS.items():
        if word in text_lower:
            score += weight
            reasons.append(f"✅ كلمة '{word}' تقلل المخاطر بنسبة {abs(weight)}%")
    
    score = max(0, min(100, score))
    
    if score >= 70:
        level = "🚨 مرتفع جداً"
        rec = "⚠️ ننصح بالفحص القانوني الدقيق قبل الشراء والتواصل مع محامٍ متخصص"
    elif score >= 40:
        level = "⚠️ متوسط"
        rec = "📋 يجب التأكد من صحة الأوراق ميدانياً ومراجعة السجل العقاري"
    else:
        level = "✅ منخفض"
        rec = "👍 العقار يبدو آمناً مع اتباع الإجراءات الروتينية"
    
    return score, level, rec, reasons[:5]  # عرض أول 5 أسباب فقط

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"🏠 مرحباً بك يا {user_name} في منظومة الدرع 🛡️\n\n"
        "أنا مساعدك الذكي لتقييم المخاطر العقارية في اليمن والخدمات التقنية.\n\n"
        "📌 *كيف تستخدم البوت:*\n"
        "• اختر من القائمة أدناه\n"
        "• أو أرسل وصف العقار مباشرة للتحليل الفوري\n\n"
        "مثال: 'أريد شراء منزل في صنعاء بصيرة مع وجود ورثة'",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True),
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # معالجة الأزرار
    if "1)" in text:
        await update.message.reply_text(
            "📝 *أرسل وصف العقار للتحليل*\n\n"
            "معلومات مفيدة للتحليل:\n"
            "• المنطقة والمدينة\n"
            "• نوع المستندات المتوفرة\n"
            "• وجود ورثة أو نزاعات\n"
            "• حالة الملكية",
            parse_mode="Markdown"
        )
    elif "2)" in text:
        await update.message.reply_text(
            "🤖 *مسارات تعلم الذكاء الاصطناعي*\n\n"
            "للحصول على دورات ومواد تعليمية في:\n"
            "• أساسيات الذكاء الاصطناعي\n"
            "• هندسة البرومبت (Prompt Engineering)\n"
            "• تطبيقات الذكاء الاصطناعي العملية\n\n"
            "📩 تواصل معنا: @fan_al_prompt"
        )
    elif "3)" in text:
        await update.message.reply_text(
            "🛠️ *خدمات التصميم والتطوير*\n\n"
            "أرسل تفاصيل مشروعك (تصميم، بناء، تطوير) وسنقوم بـ:\n"
            "1. دراسة متطلباتك\n"
            "2. تقديم خطة عمل مفصلة\n"
            "3. تحديد التكاليف والجدول الزمني\n\n"
            "يرجى إرسال وصف المشروع الآن"
        )
    elif "4)" in text:
        await update.message.reply_text(
            "🔧 *خدمات أخرى*\n\n"
            "📞 للتواصل المباشر: 778160500\n"
            "📧 البريد الإلكتروني: support@aldira.com\n"
            "💬 متاحين يومياً من 9ص - 9م"
        )
    else:
        # تحليل العقار مع معالجة الخطأ
        try:
            score, level, rec, reasons = analyze_real_estate(text)
            
            response = (
                f"🏠 *تقرير الدرع العقاري*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 *مؤشر المخاطر:* {score}/100\n"
                f"⚖️ *التقييم:* {level}\n\n"
                f"💡 *التوصية:* {rec}\n\n"
                f"📌 *الملاحظات:*\n"
            )
            
            if reasons:
                response += "\n".join(reasons[:3])  # عرض أول 3 ملاحظات فقط
                if len(reasons) > 3:
                    response += f"\n... و{len(reasons)-3} ملاحظة أخرى"
            else:
                response += "✓ لا توجد كلمات حرجة ملحوظة"
            
            response += "\n\n⚠️ هذا التقرير استرشادي وليس بديلاً عن الاستشارة القانونية"
            
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            logging.error(f"خطأ في التحليل: {e}")
            await update.message.reply_text(
                "❌ عذراً، حدث خطأ في تحليل العقار. يرجى المحاولة مرة أخرى."
            )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *مساعدة الدرع العقاري*\n\n"
        "• /start - عرض القائمة الرئيسية\n"
        "• إرسال وصف عقار - تحليل المخاطر\n"
        "• استخدام الأزرار للوصول للخدمات\n\n"
        "للتواصل المباشر: @fan_al_prompt"
    )

# تشغيل البوت
if __name__ == "__main__":
    if TOKEN == "8763108829:AAGXJH29btaEMyqGW8NXPUtmZ9egFNNyuV8":
        print("⚠️ تحذير: أنت تستخدم توكن مكشوف في الكود! استخدم متغيرات البيئة في الإنتاج.")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # إضافة المعالجات
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        print("✅ البوت يعمل الآن... (اضغط Ctrl+C للإيقاف)")
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        logging.error(f"خطأ فادح: {e}")
