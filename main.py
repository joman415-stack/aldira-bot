import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. سحب التوكن من متغيرات Railway (تأكد أن الاسم هناك BOT_TOKEN)
TOKEN = os.getenv("8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM")

# 2. بيانات التواصل الخاصة بك
CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

user_state = {}

# 3. قائمة الأسئلة (تظهر فوق الأزرار)
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

# 4. الخيارات التي ستظهر كأزرار
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

# --- دالة البداية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state[user_id] = {"step": 0, "data": {}}

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 بدء تحليل العقار الآن", callback_data="start_analysis")]
    ])

    await update.message.reply_text(
        "🛡️ **مرحباً بك في نظام الدرع العقاري**\n\n"
        "هذا النظام الاحترافي يقوم بتحليل المخاطر بناءً على 10 معايير أساسية.\n"
        "اضغط على الزر أدناه للبدء في الفحص 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- دالة إرسال الأسئلة بالأزرار ---
async def send_question(message, user_id):
    step = user_state[user_id]["step"]
    
    # تنسيق الأزرار (زرين في كل صف)
    keyboard = []
    current_options = OPTIONS[step]
    for i in range(0, len(current_options), 2):
        row = [InlineKeyboardButton(opt, callback_data=opt) for opt in current_options[i:i+2]]
        keyboard.append(row)

    await message.reply_text(
        f"❓ **السؤال {step + 1}:** {QUESTIONS[step]}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# --- محرك حساب المخاطر ---
def calculate_risk(data):
    score = 50
    reasons = []

    if data.get("doc") == "بصيرة":
        score += 15
        reasons.append("وثيقة بصيرة: تحتاج لمطابقة الأرشيف بدقة.")
    elif data.get("doc") == "عقد":
        score -= 10
        reasons.append("عقد رسمي: يرفع من موثوقية العملية.")
    elif data.get("doc") == "ملكية":
        score -= 25
        reasons.append("صك ملكية: أمان قانوني مرتفع جداً.")

    if data.get("seller") == "وريث":
        score += 25
        reasons.append("بيع ورثة: خطر تراجع أحد الورثة أو ظهور وريث جديد.")
    elif data.get("seller") == "وسيط":
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

    # تحديد التصنيف النهائي
    if score >= 75: level = "🚨 مرتفع جداً (خطر)"
    elif score >= 45: level = "⚠️ متوسط (تحتاج حذر)"
    else: level = "✅ منخفض (آمن نسبياً)"

    return score, level, reasons

# --- معالج الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "start_analysis":
        user_state[user_id] = {"step": 0, "data": {}}
        await send_question(query.message, user_id)
        return

    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state["step"]
    keys = ["doc","location","seller","papers","inherited","witnesses","plan","resale","dispute","purpose"]

    # حفظ الإجابة والانتقال للخطوة التالية
    state["data"][keys[step]] = query.data
    state["step"] += 1

    if state["step"] < len(QUESTIONS):
        await send_question(query.message, user_id)
    else:
        # حساب النتيجة النهائية
        score, level, reasons = calculate_risk(state["data"])
        
        report = (
            f"🛡️ **تقرير الدرع العقاري النهائي**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 **مؤشر المخاطر:** {score}/100\n"
            f"⚖️ **التصنيف:** {level}\n\n"
            f"📌 **ملاحظات التحليل الفني:**\n"
        )
        for r in reasons: report += f"- {r}\n"
        
        report += (
            f"\n━━━━━━━━━━━━━━━\n"
            f"💡 **للحصول على فحص ميداني وتدقيق قانوني (بريميوم):**\n"
        )

        final_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 التواصل عبر واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
            [InlineKeyboardButton("💬 تابعنا على تليجرام", url=CONTACT_TELEGRAM)],
            [InlineKeyboardButton("🌐 زيارة الموقع الرسمي", url=WEBSITE_URL)]
        ])

        await query.message.reply_text(report, reply_markup=final_keyboard, parse_mode="Markdown")
        user_state.pop(user_id)

# --- تشغيل البوت ---
def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على BOT_TOKEN في المتغيرات!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🛡️ AL-DIR'A SYSTEM IS RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
