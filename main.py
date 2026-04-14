import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv "8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM"

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

# ---------------------------
# STATE
# ---------------------------
user_state = {}

# ---------------------------
# FLOW QUESTIONS
# ---------------------------
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

# ---------------------------
# OPTIONS (STRICT BUTTON MODE)
# ---------------------------
OPTIONS = [
    ["عقد", "بصيرة", "ملكية"],
    ["مدينة", "ريف"],
    ["مالك", "وريث", "وسيط"],
    ["نعم", "لا", "غير متأكد"],
    ["نعم", "لا"],
    ["نعم", "لا"],
    ["نعم", "لا", "غير معروف"],
    ["نعم", "لا", "غير معروف"],
    ["نعم", "لا", "لا أعلم"],
    ["سكن", "استثمار", "بيع سريع"]
]

# ---------------------------
# START
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    user_state[user_id] = {
        "step": 0,
        "data": {},
        "started_at": datetime.now()
    }

    await send_question(update, user_id)

# ---------------------------
# SEND QUESTION (BUTTON ONLY)
# ---------------------------
async def send_question(update, user_id):
    step = user_state[user_id]["step"]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)]
        for opt in OPTIONS[step]
    ]

    await update.message.reply_text(
        f"🛡️ {QUESTIONS[step]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------------------
# RISK ENGINE V6
# ---------------------------
def calculate_risk(data):
    score = 50
    reasons = []

    doc = data.get("doc")
    seller = data.get("seller")

    if doc == "بصيرة":
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق قانوني")

    elif doc == "عقد":
        score -= 10
        reasons.append("عقد رسمي يقلل المخاطر")

    elif doc == "ملكية":
        score -= 25
        reasons.append("صك ملكية = أمان عالي")

    if seller == "وريث":
        score += 25
        reasons.append("بيع ورثة = خطر نزاع")

    elif seller == "وسيط":
        score += 10
        reasons.append("وسيط = يحتاج تحقق إضافي")

    elif seller == "مالك":
        score -= 15
        reasons.append("مالك مباشر = أمان أعلى")

    if data.get("papers") == "لا":
        score += 20
        reasons.append("غياب أوراق رسمية")

    if data.get("dispute") == "نعم":
        score += 25
        reasons.append("وجود نزاع سابق")

    if data.get("plan") == "لا":
        score += 15
        reasons.append("خارج المخطط")

    if score >= 75:
        level = "🚨 مرتفع"
    elif score >= 45:
        level = "⚠️ متوسط"
    else:
        level = "✅ منخفض"

    return score, level, reasons

# ---------------------------
# HANDLE CALLBACK BUTTONS ONLY
# ---------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state["step"]

    value = query.data

    keys = ["doc","location","seller","papers","inherited",
            "witnesses","plan","resale","dispute","purpose"]

    state["data"][keys[step]] = value
    state["step"] += 1

    if state["step"] < len(QUESTIONS):
        await send_question(query, user_id)
        return

    # FINAL REPORT
    score, level, reasons = calculate_risk(state["data"])

    report = f"""🛡️ تقرير الدرع العقاري V6

📊 المخاطر: {score}/100
⚖️ التصنيف: {level}

📌 التحليل:
"""

    for r in reasons:
        report += f"- {r}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
        [InlineKeyboardButton("💬 تيليجرام", url=CONTACT_TELEGRAM)],
        [InlineKeyboardButton("🌐 الموقع", url=WEBSITE_URL)]
    ])

    await query.message.reply_text(report, reply_markup=keyboard)

    user_state.pop(user_id)

# ---------------------------
# MAIN
# ---------------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    print("🛡️ AL-DIR'A V6 RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
