import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("8763108829:AAGgiw58wSFbcwwHg-VrBWckDE6V9ZQ_t-U")

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في Railway Variables")

# =========================
# STATE
# =========================
user_state = {}

QUESTIONS = [
    "📄 نوع الوثيقة",
    "📍 موقع العقار",
    "👤 صفة البائع",
    "📑 الأوراق الرسمية",
    "🧬 هل الأرض موروثة",
    "👥 وجود شهود",
    "🏗️ داخل مخطط",
    "🔁 بيع سابق",
    "⚠️ نزاع سابق",
    "💰 سبب الشراء"
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

KEYS = [
    "doc", "location", "seller", "papers", "inherited",
    "witnesses", "plan", "resale", "dispute", "purpose"
]

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_state[user_id] = {
        "step": 0,
        "data": {}
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 بدء تحليل العقار", callback_data="start_analysis")]
    ])

    await update.message.reply_text(
        "🛡️ **مرحبًا بك في نظام الدرع العقاري**\n\n"
        "سنقوم بتحليل أولي للمخاطر العقارية عبر 10 أسئلة دقيقة.\n"
        "اضغط الزر أدناه للبدء 👇",
        reply_markup=keyboard,
    )

# =========================
# SEND QUESTION
# =========================
async def send_question(chat_message, user_id):
    step = user_state[user_id]["step"]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=opt)]
        for opt in OPTIONS[step]
    ])

    await chat_message.reply_text(
        f"🛡️ {QUESTIONS[step]}",
        reply_markup=keyboard
    )

# =========================
# RISK ENGINE
# =========================
def calculate_risk(data):
    score = 50
    reasons = []

    if data["doc"] == "بصيرة":
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق قانوني")

    elif data["doc"] == "عقد":
        score -= 10
        reasons.append("عقد رسمي يقلل المخاطر")

    elif data["doc"] == "ملكية":
        score -= 25
        reasons.append("صك ملكية = أمان أعلى")

    if data["seller"] == "وريث":
        score += 25
        reasons.append("بيع من وريث = احتمال نزاع")

    elif data["seller"] == "وسيط":
        score += 10
        reasons.append("وسيط = يلزم تحقق إضافي")

    elif data["seller"] == "مالك":
        score -= 15
        reasons.append("مالك مباشر = أمان أفضل")

    if data["papers"] == "لا":
        score += 20
        reasons.append("عدم وجود أوراق رسمية")

    if data["dispute"] == "نعم":
        score += 25
        reasons.append("وجود نزاع سابق")

    if data["plan"] == "لا":
        score += 15
        reasons.append("العقار خارج المخطط")

    score = max(0, min(100, score))

    if score >= 75:
        level = "🚨 مرتفع"
    elif score >= 45:
        level = "⚠️ متوسط"
    else:
        level = "✅ منخفض"

    return score, level, reasons

# =========================
# CALLBACK HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # بدء التحليل
    if query.data == "start_analysis":
        if user_id not in user_state:
            user_state[user_id] = {"step": 0, "data": {}}
        await send_question(query.message, user_id)
        return

    # حماية من الجلسة المنتهية
    if user_id not in user_state:
        await query.message.reply_text(
            "⚠️ انتهت الجلسة. أرسل /start لبدء تحليل جديد."
        )
        return

    state = user_state[user_id]
    step = state["step"]

    # حماية من الضغط الزائد
    if step >= len(QUESTIONS):
        await query.message.reply_text("⚠️ انتهى التحليل بالفعل.")
        return

    state["data"][KEYS[step]] = query.data
    state["step"] += 1

    # السؤال التالي
    if state["step"] < len(QUESTIONS):
        await send_question(query.message, user_id)
        return

    # التقرير النهائي
    score, level, reasons = calculate_risk(state["data"])

    report = (
        "🛡️ **تقرير الدرع العقاري**\n\n"
        f"📊 درجة المخاطر: **{score}/100**\n"
        f"⚖️ التصنيف: **{level}**\n\n"
        "📌 أسباب التقييم:\n"
    )

    for r in reasons:
        report += f"- {r}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
        [InlineKeyboardButton("💬 تيليجرام", url=CONTACT_TELEGRAM)],
        [InlineKeyboardButton("🌐 الموقع", url=WEBSITE_URL)]
    ])

    await query.message.reply_text(report, reply_markup=keyboard)

    user_state.pop(user_id, None)

# =========================
# MAIN
# =========================
def main():
    print("🛡️ SYSTEM STARTING...")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ BOT IS RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
