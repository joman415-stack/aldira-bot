import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8763108829:AAGgiw58wSFbcwwHg-VrBWckDE6V9ZQ_t-U"

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

    # صفة البائع
    if "وريث" in t:
        return "2"
    if "مالك" in t:
        return "1"
    if "وسيط" in t:
        return "3"

    # نعم / لا
    if "نعم" in t:
        return "1"
    if "لا" in t:
        return "2"

    if "لا أعلم" in t or "غير" in t:
        return "3"

    return t


def calculate_risk(data: dict):
    score = 50
    reasons = []

    # الوثيقة
    doc = data.get("doc", "")

    if "بصيرة" in doc:
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق")

    if "عقد" in doc:
        score -= 10
        reasons.append("عقد رسمي يقلل المخاطر")

    if "ملكية" in doc:
        score -= 20
        reasons.append("صك ملكية = أمان أعلى")

    # البائع
    seller = data.get("seller", "")

    if seller == "2":
        score += 25
        reasons.append("ورثة = احتمال نزاع")

    if seller == "3":
        score += 10
        reasons.append("وسيط = يحتاج تحقق")

    if seller == "1":
        score -= 15
        reasons.append("مالك مباشر = أمان أعلى")

    # نزاع
    if data.get("dispute") == "1":
        score += 25
        reasons.append("وجود نزاع سابق")

    # أوراق
    if data.get("papers") == "2":
        score += 15
        reasons.append("عدم وجود أوراق رسمية")

    # التصنيف
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
        "سنجمع بيانات العقار عبر 10 أسئلة منظمة للحصول على تحليل دقيق.\n\n"
        + QUESTIONS[0]
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = normalize(update.message.text)

    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "data": {}}

    state = user_state[user_id]
    step = state["step"]

    if step >= len(QUESTIONS):
        return

    # حفظ البيانات حسب المرحلة
    if step == 0:
        state["data"]["doc"] = text
    elif step == 1:
        state["data"]["location"] = text
    elif step == 2:
        state["data"]["seller"] = text
    elif step == 3:
        state["data"]["papers"] = text
    elif step == 4:
        state["data"]["inherited"] = text
    elif step == 5:
        state["data"]["witnesses"] = text
    elif step == 6:
        state["data"]["plan"] = text
    elif step == 7:
        state["data"]["resale"] = text
    elif step == 8:
        state["data"]["dispute"] = text
    elif step == 9:
        state["data"]["purpose"] = text

    state["step"] += 1

    # استمرار الأسئلة
    if state["step"] < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[state["step"]])
        return

    # التحليل النهائي
    score, level, reasons = calculate_risk(state["data"])

    report = f"""🛡️ تقرير الدرع العقاري

📊 درجة المخاطر: {score}/100
⚖️ التصنيف: {level}

📌 الأسباب:
"""

    for r in reasons:
        report += f"- {r}\n"

    await update.message.reply_text(report)

    user_state.pop(user_id)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🛡️ AL-DIR'A CLEAN SYSTEM RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
