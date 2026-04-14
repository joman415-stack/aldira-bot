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
TOKEN = "8763108829:AAGgiw58wSFbcwwHg-VrBWckDE6V9ZQ_t-U"

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

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
        "🛡️ مرحبًا بك في نظام الدرع العقاري\n\n"
        "سنقوم بتحليل المخاطر العقارية عبر 10 أسئلة دقيقة.\n"
        "اضغط للبدء 👇",
        reply_markup=keyboard
    )

# =========================
# SEND QUESTION
# =========================
async def send_question(message, user_id):
    step = user_state[user_id]["step"]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=opt)]
        for opt in OPTIONS[step]
    ])

    await message.reply_text(
        f"🛡️ {QUESTIONS[step]}",
        reply_markup=keyboard
    )

# =========================
# RISK ENGINE
# =========================
def calculate_risk(data):
    score = 50
    reasons = []

    if data.get("doc") == "بصيرة":
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق قانوني")

    elif data.get("doc") == "عقد":
        score -= 10
        reasons.append("عقد رسمي يقلل المخاطر")

    elif data.get("doc") == "ملكية":
        score -= 25
        reasons.append("صك ملكية = أمان أعلى")

    if data.get("seller") == "وريث":
        score += 25
        reasons.append("بيع من وريث = احتمال نزاع")

    elif data.get("seller") == "وسيط":
        score += 10
        reasons.append("وسيط = يلزم تحقق إضافي")

    elif data.get("seller") == "مالك":
        score -= 15
        reasons.append("مالك مباشر = أمان أفضل")

    if data.get("papers") == "لا":
        score += 20
        reasons.append("عدم وجود أوراق رسمية")

    if data.get("dispute") == "نعم":
        score += 25
        reasons.append("وجود نزاع سابق")

    if data.get("plan") == "لا":
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

    if query.data == "start_analysis":
        if user_id not in user_state:
            user_state[user_id] = {"step": 0, "data": {}}
        await send_question(query.message, user_id)
        return

    if user_id not in user_state:
        await query.message.reply_text("⚠️ أرسل /start لبدء التحليل")
        return

    state = user_state[user_id]
    step = state["step"]

    state["data"][KEYS[step]] = query.data
    state["step"] += 1

    if state["step"] < len(QUESTIONS):
        await send_question(query.message, user_id)
        return

    score, level, reasons = calculate_risk(state["data"])

    report = (
        "🛡️ تقرير الدرع العقاري\n\n"
        f"📊 درجة المخاطر: {score}/100\n"
        f"⚖️ التصنيف: {level}\n\n"
        "📌 الأسباب:\n"
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
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🛡️ BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
