import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("8763108829:AAHXLxqTlB8xJRjr2_LZxwYUwPUGtJbFIdM")

CONTACT_PHONE = "967778160500"
CONTACT_TELEGRAM = "https://t.me/fan_al_prompt"
WEBSITE_URL = "https://al-dira.com"

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   user_id = update.message.from_user.id
   user_state[user_id] = {"step": 0, "data": {}}
   keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 بدء تحليل العقار", callback_data="start")]])
   await update.message.reply_text("🛡️ مرحبًا بك في نظام الدرع العقاري\n\nهذا النظام يقوم بتحليل المخاطر العقارية عبر 10 أسئلة دقيقة.\nاضغط للبدء 👇", reply_markup=keyboard)

async def send_question(message, user_id):
   step = user_state[user_id]["step"]
   keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in OPTIONS[step]]
   await message.reply_text(f"🛡️ {QUESTIONS[step]}", reply_markup=InlineKeyboardMarkup(keyboard))

def calculate_risk(data):
   score = 50
   reasons = []
   if data.get("doc") == "بصيرة":
       score += 15
       reasons.append("وثيقة بصيرة تحتاج تحقق")
   elif data.get("doc") == "عقد":
       score -= 10
       reasons.append("عقد رسمي يقلل المخاطر")
   elif data.get("doc") == "ملكية":
       score -= 25
       reasons.append("صك ملكية = أمان أعلى")
   if data.get("seller") == "وريث":
       score += 25
       reasons.append("بيع ورثة = خطر نزاع")
   elif data.get("seller") == "وسيط":
       score += 10
       reasons.append("وسيط يحتاج تحقق")
   elif data.get("seller") == "مالك":
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
   level = "🚨 مرتفع" if score >= 75 else "⚠️ متوسط" if score >= 45 else "✅ منخفض"
   return score, level, reasons

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
   query = update.callback_query
   await query.answer()
   user_id = query.from_user.id
   if query.data == "start":
       await send_question(query.message, user_id)
       return
   if user_id not in user_state:
       return
   state = user_state[user_id]
   step = state["step"]
   keys = ["doc","location","seller","papers","inherited","witnesses","plan","resale","dispute","purpose"]
   state["data"][keys[step]] = query.data
   state["step"] += 1
   if state["step"] < len(QUESTIONS):
       await send_question(query.message, user_id)
       return
   score, level, reasons = calculate_risk(state["data"])
   report = f"🛡️ تقرير الدرع العقاري\n\n📊 المخاطر: {score}/100\n⚖️ التصنيف: {level}\n\n📌 التحليل:\n"
   for r in reasons:
       report += f"- {r}\n"
   keyboard = InlineKeyboardMarkup([
       [InlineKeyboardButton("📞 واتساب", url=f"https://wa.me/{CONTACT_PHONE}")],
       [InlineKeyboardButton("💬 تيليجرام", url=CONTACT_TELEGRAM)],
       [InlineKeyboardButton("🌐 الموقع", url=WEBSITE_URL)]
   ])
   await query.message.reply_text(report, reply_markup=keyboard)
   user_state.pop(user_id)

def main():
   app = Application.builder().token(TOKEN).build()
   app.add_handler(CommandHandler("start", start))
   app.add_handler(CallbackQueryHandler(button_handler))
   print("🛡️ SYSTEM RUNNING...")
   app.run_polling()

if __name__ == "__main__":
   main()
