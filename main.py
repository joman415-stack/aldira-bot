import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM"

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state[user_id] = {"step": 0, "data": {}}

    await update.message.reply_text(
        "🛡️ مرحبًا بك في نظام الدرع العقاري\n\n"
        "سنقوم بتحليل العقار عبر 10 أسئلة دقيقة للحصول على تقييم مخاطر احترافي.\n\n"
        "لنبدأ 👇\n" + QUESTIONS[0]
    )


def calculate_risk(data: dict):
    score = 50
    reasons = []

    # 📄 الوثيقة
    if "بصيرة" in data.get("doc", ""):
        score += 15
        reasons.append("وثيقة بصيرة تحتاج تحقق قوي")

    if "عقد" in data.get("doc", ""):
        score -= 10
        reasons.append("وجود عقد رسمي يقلل المخاطر")

    if "ملكية" in data.get("doc", ""):
        score -= 20
        reasons.append("صك ملكية = أمان أعلى")

    # 👤 البائع
    if "وريث" in data.get("seller", ""):
        score += 25
        reasons.append("بيع ورثة = احتمال نزاع")

    if "وسيط" in data.get("seller", ""):
        score += 10
        reasons.append("وسيط = يحتاج تحقق إضافي")

    if "مالك" in data.get("seller", ""):
        score -= 15
        reasons.append("مالك مباشر = أمان أعلى")

    # ⚠️ النزاعات
    if data.get("dispute") == "نعم":
        score += 25
        reasons.append("وجود نزاع سابق")

    # 📑 الأوراق
    if data.get("mortgage") == "لا":
        score += 10
        reasons.append("عدم وجود أوراق رسمية يزيد المخاطر")

    # ⚖️ التصنيف
    if score >= 75:
        level = "🚨 مرتفع"
    elif score >= 45:
        level = "⚠️ متوسط"
    else:
        level = "✅ منخفض"

    return score, level, reasons


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "data": {}}

    state = user_state[user_id]
    step = state["step"]

    # حفظ الإجابة حسب الترتيب
    if step == 0:
        state["data"]["doc"] = text
    elif step == 1:
        state["data"]["location"] = text
    elif step == 2:
        state["data"]["seller"] = text
    elif step == 3:
        state["data"]["mortgage"] = text
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

    # إذا لم تنتهِ الأسئلة
    if state["step"] < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[state["step"]])
        return

    # 🧠 التحليل النهائي
    score, level, reasons = calculate_risk(state["data"])

    report = f"""🛡️ تقرير الدرع العقاري

📊 درجة المخاطر: {score}/100
⚖️ التصنيف: {level}

📌 الأسباب:
"""

    for r in reasons:
        report += f"- {r}\n"

    report += "\n📲 للتواصل: واتساب / تيليجرام"

    await update.message.reply_text(report)

    user_state.pop(user_id)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🛡️ AL-DIR'A 10 QUESTIONS SYSTEM RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
