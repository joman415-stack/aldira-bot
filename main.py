import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# تفعيل التسجيل للأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. سحب التوكن من متغيرات Railway
TOKEN = os.getenv("8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM")

# 2. بيانات التواصل
CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

# استخدام dict عادي (لكن في الإنتاج استخدم قاعدة بيانات)
user_state = {}

# 3. الأسئلة والخيارات
QUESTIONS = [
    "نوع الوثيقة المقدمة للعقار:",
    "موقع العقار الحالي:",
    "ما هي صفة البائع؟",
    "هل توجد أوراق رسمية مكتملة؟",
    "هل الأرض موروثة (وراثة)؟",
    "هل يوجد شهود على عملية البيع؟",
    "هل العقار داخل مخطط معتمد؟",
    "هل تم بيع العقار سابقاً؟",
    "هل يوجد أي نزاع سابق على الأرض؟",
    "ما هو هدفك من الشراء؟"
]

OPTIONS = [
    ["عقد", "بصيرة", "ملكية"],
    ["مدينة", "ريف"],
    ["مالك", "وريث", "وسيط"],
    ["نعم", "لا"],
    ["نعم", "لا"],
    ["نعم", "لا"],
    ["نعم", "لا"],
    ["نعم", "لا"],
    ["نعم", "لا"],
    ["سكن", "استثمار", "بيع سريع"]
]

# مفاتيح حفظ البيانات
KEYS = ["doc", "location", "seller", "papers", "inherited", 
        "witnesses", "plan", "resale", "dispute", "purpose"]

# --- دالة البداية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state[user_id] = {"step": 0, "data": {}}
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 بدء تحليل العقار الآن", callback_data="start_analysis")]
    ])
    
    await update.message.reply_text(
        "🛡️ *مرحباً بك في نظام الدرع العقاري*\n\n"
        "هذا النظام الاحترافي يقوم بتحليل المخاطر بناءً على 10 معايير أساسية.\n"
        "اضغط على الزر أدناه للبدء في الفحص 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- إرسال السؤال التالي ---
async def send_question(message, user_id):
    step = user_state[user_id]["step"]
    
    if step >= len(QUESTIONS):
        return await show_results(message, user_id)
    
    # إنشاء الأزرار بشكل صحيح (كل زر في صف منفصل للأمان)
    keyboard = []
    for opt in OPTIONS[step]:
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"ans_{step}_{opt}")])
    
    await message.reply_text(
        f"❓ *السؤال {step + 1} من {len(QUESTIONS)}:*\n{QUESTIONS[step]}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# --- معالج الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # بدء التحليل
    if data == "start_analysis":
        user_state[user_id] = {"step": 0, "data": {}}
        await send_question(query.message, user_id)
        return
    
    # التحقق من وجود المستخدم في الحالة
    if user_id not in user_state:
        await query.message.reply_text(
            "⚠️ انتهت الجلسة. اضغط /start للبدء من جديد."
        )
        return
    
    # معالجة الإجابة
    if data.startswith("ans_"):
        try:
            parts = data.split("_", 2)
            step = int(parts[1])
            answer = parts[2]
            
            state = user_state[user_id]
            
            # التحقق من تطابق الخطوة
            if step != state["step"]:
                await query.answer("⚠️ خطأ في التسلسل!", show_alert=True)
                return
            
            # حفظ الإجابة
            state["data"][KEYS[step]] = answer
            state["step"] += 1
            
            # الانتقال للسؤال التالي أو النتيجة
            if state["step"] < len(QUESTIONS):
                await send_question(query.message, user_id)
            else:
                await show_results(query.message, user_id)
                
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            await query.message.reply_text("❌ حدث خطأ. اضغط /start للمحاولة مرة أخرى.")

# --- عرض النتائج ---
async def show_results(message, user_id):
    data = user_state[user_id]["data"]
    score, level, reasons = calculate_risk(data)
    
    report = (
        f"🛡️ *تقرير الدرع العقاري النهائي*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 *مؤشر المخاطر:* {score}/100\n"
        f"⚖️ *التصنيف:* {level}\n\n"
        f"📌 *ملاحظات التحليل الفني:*\n"
    )
    for r in reasons:
        report += f"• {r}\n"
    
    report += (
        f"\n━━━━━━━━━━━━━━━\n"
        f"💡 *للحصول على فحص ميداني وتدقيق قانوني (بريميوم):*"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 التواصل عبر واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
        [InlineKeyboardButton("💬 تابعنا على تليجرام", url=CONTACT_TELEGRAM)],
        [InlineKeyboardButton("🌐 زيارة الموقع الرسمي", url=WEBSITE_URL)],
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="start_analysis")]
    ])
    
    await message.reply_text(report, reply_markup=keyboard, parse_mode="Markdown")
    
    # تنظيف الحالة
    user_state.pop(user_id, None)

# --- محرك حساب المخاطر ---
def calculate_risk(data):
    score = 50
    reasons = []
    
    doc = data.get("doc", "")
    if doc == "بصيرة":
        score += 15
        reasons.append("وثيقة بصيرة: تحتاج لمطابقة الأرشيف بدقة.")
    elif doc == "عقد":
        score -= 10
        reasons.append("عقد رسمي: يرفع من موثوقية العملية.")
    elif doc == "ملكية":
        score -= 25
        reasons.append("صك ملكية: أمان قانوني مرتفع جداً.")
    
    seller = data.get("seller", "")
    if seller == "وريث":
        score += 25
        reasons.append("بيع ورثة: خطر تراجع أحد الورثة أو ظهور وريث جديد.")
    elif seller == "وسيط":
        score += 10
        reasons.append("وسيط: يجب التأكد من صحة الوكالة القانونية.")
    
    if data.get("papers") == "لا":
        score += 20
        reasons.append("نقص الأوراق الرسمية يزيد من احتمالية النزاع.")
    
    if data.get("dispute") == "نعم":
        score += 30
        reasons.append("نزاع سابق: الأرض عليها 'ملاحقة' أو إشكال قديم.")
    
    if data.get("plan") == "لا":
        score += 15
        reasons.append("خارج المخطط: قد تواجه مشاكل في الخدمات أو التراخيص.")
    
    if score >= 75:
        level = "🚨 مرتفع جداً (خطر)"
    elif score >= 45:
        level = "⚠️ متوسط (تحتاج حذر)"
    else:
        level = "✅ منخفض (آمن نسبياً)"
    
    return score, level, reasons

# --- معالج الأخطاء ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى لاحقاً."
        )

# --- التشغيل ---
def main():
    if not TOKEN:
        logger.error("❌ خطأ: لم يتم العثور على BOT_TOKEN في المتغيرات!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    
    logger.info("🛡️ AL-DIR'A SYSTEM IS RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
