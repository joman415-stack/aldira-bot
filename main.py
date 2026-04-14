import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ مهم: ضع التوكن في Railway باسم BOT_TOKEN
TOKEN = os.getenv "8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM"

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

# ---------------------------
# STATE
# ---------------------------
user_state = {}

# ---------------------------
# QUESTIONS
# ---------------------------
QUESTIONS = [
    "📄 نوع الوثيقة:",
    "📍 موقع العقار:",
    "👤 صفة البائع:",
    "📑 الأوراق الرسمية:",
    "🧬 هل الأرض موروثة:",
    "👥 وجود شهود:",
    "🏗️ داخل مخطط:",
    "🔁 بيع سابق:",
    "⚠️ نزاع سابق:",
    "💰 سبب الشراء:"
]

# ---------------------------
# OPTIONS (Buttons)
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
# NORMALIZE INPUT
# ---------------------------
def normalize(text: str):
    t = text.strip().lower()

    if t in ["عقد", "بصيرة", "ملكية", "مالك", "وريث", "وسيط",
             "نعم", "لا", "غير متأكد", "غير معروف", "لا أعلم",
             "سكن", "استثمار", "بيع سريع"]:
        return t

    return t

# ---------------------------
# RISK ENGINE
# ---------------------------
def calculate_risk(data: dict):
    score = 50
    reasons = []

    doc = data.get("doc", "")
    seller = data.get("seller", "")

    if doc == "بصيرة":
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق قانوني")

    elif doc == "عقد":
        score -= 10
        reasons.append("عقد رسمي يقلل المخاطر")

    elif doc == "ملكية":
        score -= 25
        reasons.append("صك ملكية = أمان أعلى")

    if seller == "وريث":
        score += 25
        reasons.append("بيع ورثة = احتمال نزاع")

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
# START
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    user_state[user_id] = {
        "step": 0,
        "data": {},
        "started_at": datetime.now()
    }

    await update.message.reply_text(
        "🛡️ مرحبًا بك في نظام الدرع العقاري\n\n"
        "سنقوم بتحليل العقار عبر 10 أسئلة دقيقة للحصول على تقييم احترافي.\n\n"
        + QUESTIONS[0]
    )

# ---------------------------
# HANDLE MESSAGES
# ---------------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "data": {}}

    state = user_state[user_id]
    step = state["step"]

    if step >= len(QUESTIONS):
        return

    text = normalize(update.message.text)

    keys = ["doc", "location", "seller", "papers", "inherited",
            "witnesses", "plan", "resale", "dispute", "purpose"]

    state["data"][keys[step]] = text
    state["step"] += 1

    # next question
    if state["step"] < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[state["step"]])
        return

    # final analysis
    score, level, reasons = calculate_risk(state["data"])

    report = f"""🛡️ تقرير الدرع العقاري V4

📊 درجة المخاطر: {score}/100
⚖️ التصنيف: {level}

📌 التحليل:
"""

    for r in reasons:
        report += f"- {r}\n"

    keyboard = [
        [InlineKeyboardButton("📞 واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
        [InlineKeyboardButton("💬 تيليجرام", url=CONTACT_TELEGRAM)],
        [InlineKeyboardButton("🌐 الموقع", url=WEBSITE_URL)]
    ]

    await update.message.reply_text(
        report,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    user_state.pop(user_id)

# ---------------------------
# MAIN
# ---------------------------
def main():
    if not TOKEN:
        print("❌ BOT_TOKEN غير موجود في البيئة")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🛡️ AL-DIR'A V4 RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
