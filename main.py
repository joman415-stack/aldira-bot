import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# التوكن
TOKEN = os.getenv("8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM")

# 📞 بيانات التواصل (مصَححة)
CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

user_state = {}

QUESTIONS = [
    "📄 ما نوع الوثيقة؟ (عقد / بصيرة / ملكية / غير معروف)",
    "📍 ما موقع العقار؟",
    "👤 ما صفة البائع؟ (مالك / وريث / وسيط)",
    "📑 هل توجد أوراق رسمية؟ (نعم / لا / غير متأكد)",
    "🧬 هل الأرض موروثة؟ (نعم / لا)",
    "👥 هل يوجد شهود؟ (نعم / لا)",
    "🏗️ هل الأرض داخل مخطط معتمد؟ (نعم / لا / غير معروف)",
    "🔁 هل تم البيع أكثر من مرة؟ (نعم / لا / غير معروف)",
    "⚠️ هل يوجد نزاع سابق؟ (نعم / لا / لا أعلم)",
    "💰 ما سبب الشراء؟ (سكن / استثمار / بيع سريع)"
]

def normalize(text: str):
    t = text.strip().lower()

    if any(x in t for x in ["وريث", "وارث", "ورثة", "الورثة"]): 
        return "2"
    if any(x in t for x in ["مالك", "صاحب", "المالك"]): 
        return "1"
    if any(x in t for x in ["وسيط", "وكيل", "سمسار"]): 
        return "3"

    if any(x in t for x in ["نعم", "ايه", "yes", "أكيد"]): 
        return "1"
    if any(x in t for x in ["لا", "no", "لأ", "لاء"]): 
        return "2"
    if any(x in t for x in ["لا أعلم", "لا اعرف", "غير متأكد"]): 
        return "3"

    return t


def calculate_risk(data: dict):
    score = 50
    reasons = []

    doc = data.get("doc", "")
    seller = data.get("seller", "")

    if "بصيرة" in doc:
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق")

    if "عقد" in doc:
        score -= 10
        reasons.append("عقد رسمي يقلل المخاطر")

    if "ملكية" in doc:
        score -= 20
        reasons.append("صك ملكية = أمان أعلى")

    if seller == "2":
        score += 25
        reasons.append("ورثة = احتمال نزاع")

    if seller == "3":
        score += 10
        reasons.append("وسيط = يحتاج تحقق")

    if seller == "1":
        score -= 15
        reasons.append("مالك مباشر = أمان أعلى")

    if data.get("dispute") == "1":
        score += 25
        reasons.append("وجود نزاع سابق")

    if data.get("papers") == "2":
        score += 15
        reasons.append("عدم وجود أوراق رسمية")

    if score >= 75:
        level = "🚨 مرتفع"
    elif score >= 45:
        level = "⚠️ متوسط"
    else:
        level = "✅ منخفض"

    return score, level, reasons


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state[user_id] = {"step": 0, "data": {}}

    await update.message.reply_text(
        "🛡️ مرحبًا بك في نظام الدرع العقاري\n\n"
        "نقوم بتحليل العقار عبر 10 أسئلة دقيقة للحصول على تقييم مخاطر احترافي.\n\n"
        + QUESTIONS[0]
    )


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

    if state["step"] < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[state["step"]])
        return

    score, level, reasons = calculate_risk(state["data"])

    report = f"""🛡️ تقرير الدرع العقاري

📊 درجة المخاطر: {score}/100
⚖️ التصنيف: {level}

📌 الأسباب:
"""

    for r in reasons:
        report += f"- {r}\n"

    # 🔥 أزرار التواصل المصححة
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


def main():
    if not TOKEN:
        print("خطأ: BOT_TOKEN غير موجود")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🛡️ AL-DIR'A SYSTEM RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
