import os
import json
import logging
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters
)

# =========================
# 🔥 التوكن
# =========================
TOKEN = "8763108829:AAGl10eR5hGJCnBgkF2v2lCWY7Ut7hWurnc"
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود")

ADMIN_ID = 5068122021
DATA_FILE = "data/clients.json"

# =========================
# 🌐 سيرفر Render
# =========================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# =========================
# 📊 logging
# =========================
logging.basicConfig(level=logging.INFO)

def error_handler(update, context):
    logging.error("BOT ERROR", exc_info=context.error)

# =========================
# 🧠 NLP بسيط (نعم / لا)
# =========================
def smart_nlu(text):
    if not text:
        return None

    t = text.lower().strip()
    t = re.sub(r'(.)\1+', r'\1', t)

    yes = ["yes", "y", "نعم", "ايوه", "أيوه", "تمام", "أكيد", "صح", "موافق", "ok"]
    no = ["no", "n", "لا", "لالا", "مو", "مش", "ما في", "غير صحيح"]

    for w in yes:
        if w in t:
            return "yes"

    for w in no:
        if w in t:
            return "no"

    return None

# =========================
# 🧠 محرك التحليل العقاري الذكي
# =========================
def real_estate_ai(text, doc_type=None, inheritance=None):
    t = (text or "").lower()

    score = 60
    flags = []

    high = ["نزاع", "محكمة", "مغتصبة", "متنازع", "قضية"]
    medium = ["بصيرة", "غير موثق", "ورثة", "بدون تسجيل"]
    safe = ["سند ملكية", "مسجل", "موثق", "هيئة"]

    for w in high:
        if w in t:
            score -= 25
            flags.append("خطر قانوني")

    for w in medium:
        if w in t:
            score -= 15
            flags.append("توثيق ضعيف")

    for w in safe:
        if w in t:
            score += 15
            flags.append("توثيق قوي")

    if doc_type:
        d = doc_type.lower()
        if "سند" in d:
            score += 20
        if "بصيرة" in d:
            score -= 10

    if inheritance == "inherit":
        score -= 10

    score = max(5, min(100, score))

    if score >= 75:
        risk = "منخفض 🟢"
        action = "آمن مبدئياً"
    elif score >= 55:
        risk = "متوسط 🟡"
        action = "يحتاج مراجعة"
    elif score >= 35:
        risk = "مرتفع 🟠"
        action = "يحتاج مختص"
    else:
        risk = "حرج 🔴"
        action = "إيقاف قبل الشراء"

    return {
        "score": score,
        "risk": risk,
        "action": action,
        "flags": list(set(flags))
    }

# =========================
# 💾 بيانات
# =========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================
# 📌 الحالات
# =========================
NAME, SERVICE, LOCATION, OWNER, DOC_TYPE, DOC_DATE, ISSUER, INHERITANCE, PROBLEMS = range(9)

# =========================
# 🟢 رسالة البداية
# =========================
WELCOME_MSG = """
🛡️ نظام الدرع v23

اختر الخدمة:
"""

# =========================
# 🔁 تنظيف
# =========================
def reset(context):
    context.user_data.clear()

# =========================
# 🚀 البداية
# =========================
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
        [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")]
    ]
    update.message.reply_text(WELCOME_MSG, reply_markup=InlineKeyboardMarkup(keyboard))
    return SERVICE

def service(update, context):
    q = update.callback_query
    q.answer()
    context.user_data["service"] = q.data
    q.edit_message_text("✏️ الاسم الكامل:")
    return NAME

# =========================
# 👤 الاسم (بدون توقف عند الخطأ)
# =========================
def name(update, context):
    text = update.message.text
    if len(text) < 3:
        update.message.reply_text("⚠️ الاسم قصير، أعد الإرسال")
        return NAME

    context.user_data["name"] = text
    update.message.reply_text("📍 الموقع:")
    return LOCATION

def location(update, context):
    context.user_data["location"] = update.message.text
    update.message.reply_text("👤 اسم المالك:")
    return OWNER

def owner(update, context):
    context.user_data["owner"] = update.message.text
    update.message.reply_text("📄 نوع الوثيقة:")
    return DOC_TYPE

def doc_type(update, context):
    context.user_data["doc_type"] = update.message.text
    update.message.reply_text("📅 تاريخ الإصدار:")
    return DOC_DATE

# =========================
# 📅 التاريخ (ملاحظة واضحة)
# =========================
def doc_date(update, context):
    text = update.message.text

    try:
        datetime.strptime(text, "%Y-%m-%d")
    except:
        update.message.reply_text(
            "📅 يرجى إرسال تاريخ الإصدار بصيغة:\n"
            "(سنة-شهر-يوم)\n"
            "مثال: 2026-04-19"
        )
        return DOC_DATE

    context.user_data["doc_date"] = text
    update.message.reply_text("🏛️ الجهة المصدرة:")
    return ISSUER

def issuer(update, context):
    context.user_data["issuer"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("شراء", callback_data="buy")],
        [InlineKeyboardButton("ورث", callback_data="inherit")]
    ]
    update.message.reply_text("⚖️ نوع الحيازة:", reply_markup=InlineKeyboardMarkup(keyboard))
    return INHERITANCE

def inheritance(update, context):
    q = update.callback_query
    q.answer()
    context.user_data["inheritance"] = q.data

    keyboard = [
        [InlineKeyboardButton("لا يوجد مشاكل", callback_data="no")],
        [InlineKeyboardButton("يوجد مشاكل", callback_data="yes")]
    ]
    q.edit_message_text("⚠️ هل توجد مشاكل؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return PROBLEMS

# =========================
# 🧠 التحليل النهائي
# =========================
def problems(update, context):
    q = update.callback_query
    q.answer()

    context.user_data["problems"] = q.data

    result = real_estate_ai(
        text=context.user_data.get("issuer", ""),
        doc_type=context.user_data.get("doc_type"),
        inheritance=context.user_data.get("inheritance")
    )

    score = result["score"]
    risk = result["risk"]
    action = result["action"]

    msg = f"""
🛡️ تحليل الدرع الذكي

📊 النتيجة: {score}%
⚖️ الحالة: {risk}

🧠 التوصية:
{action}

⏳ النتيجة النهائية خلال 24 ساعة
📞 سيتم تحويلك للمختص
"""

    keyboard = [
        [InlineKeyboardButton("📱 واتساب", url="https://wa.me/967778160500")],
        [InlineKeyboardButton("💬 تليجرام", url="https://t.me/fan_al_prompt")],
        [InlineKeyboardButton("🌐 الموقع", url="https://sites.google.com/view/aldira-yemen")]
    ]

    q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    # حفظ
    data = load_data()
    uid = str(q.from_user.id)
    data.setdefault(uid, []).append(context.user_data.copy())
    save_data(data)

    # أدمن
    try:
        context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    except:
        pass

    reset(context)
    return ConversationHandler.END

# =========================
# ❌ إلغاء
# =========================
def cancel(update, context):
    update.message.reply_text("❌ تم الإلغاء")
    reset(context)
    return ConversationHandler.END

# =========================
# 🚀 التشغيل
# =========================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_error_handler(error_handler)

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SERVICE: [CallbackQueryHandler(service)],
            NAME: [MessageHandler(Filters.text, name)],
            LOCATION: [MessageHandler(Filters.text, location)],
            OWNER: [MessageHandler(Filters.text, owner)],
            DOC_TYPE: [MessageHandler(Filters.text, doc_type)],
            DOC_DATE: [MessageHandler(Filters.text, doc_date)],
            ISSUER: [MessageHandler(Filters.text, issuer)],
            INHERITANCE: [CallbackQueryHandler(inheritance)],
            PROBLEMS: [CallbackQueryHandler(problems)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
