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
# 🌐 سيرفر وهمي لـ Render
# =========================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# =========================
# 🧾 logging
# =========================
logging.basicConfig(level=logging.INFO)

def error_handler(update, context):
    logging.error("BOT ERROR", exc_info=context.error)

# =========================
# 📦 البيانات
# =========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================
# 🔢 الحالات
# =========================
NAME, SERVICE, LOCATION, OWNER, DOC_TYPE, DOC_NUM, DOC_DATE, ISSUER, INHERITANCE, PROBLEMS = range(10)

# =========================
# 🛡️ رسالة البداية
# =========================
WELCOME_MSG = """
🛡️ نظام الدرع v23 - اليمن

أهلاً بك في نظام تحليل المخاطر العقارية

📊 الخدمة:
تحليل أولي + تقييم مخاطر

⚠️ النتيجة خلال ثواني (أولي) + تقرير نهائي خلال 24 ساعة

🔽 اختر الخدمة:
"""

# =========================
# 🧠 تنظيف
# =========================
def reset_user(context):
    context.user_data.clear()

# =========================
# 🧪 التحقق من الإدخال
# =========================
def validate(update, field):
    text = update.message.text.strip()

    if not text:
        update.message.reply_text("⚠️ لا يمكن تركه فارغ")
        return None

    if field == "name":
        if len(text) < 3:
            update.message.reply_text("⚠️ الاسم يجب أن يكون 3 أحرف على الأقل")
            return None

    if field == "doc_num":
        if not text.isdigit():
            update.message.reply_text("⚠️ رقم الوثيقة أرقام فقط")
            return None

    if field == "date":
        try:
            datetime.strptime(text, "%Y-%m-%d")
        except:
            update.message.reply_text(
                "📅 يرجى إرسال تاريخ الإصدار بصيغة:\n"
                "YYYY-MM-DD\n"
                "📌 مثال: 2026-04-19"
            )
            return None

    return text

# =========================
# 🚀 البداية
# =========================
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
        [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")],
        [InlineKeyboardButton("🔧 استشارة فنية", callback_data="technical")]
    ]

    update.message.reply_text(
        WELCOME_MSG,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SERVICE

# =========================
# 📌 اختيار الخدمة
# =========================
def service_selected(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["service"] = query.data
    query.edit_message_text("✏️ أرسل اسمك الكامل:")
    return NAME

# =========================
# 👤 الاسم
# =========================
def get_name(update, context):
    text = validate(update, "name")
    if not text:
        return NAME

    context.user_data["name"] = text
    update.message.reply_text("📍 المحافظة:")
    return LOCATION

# =========================
# 📍 الموقع
# =========================
def get_location(update, context):
    text = validate(update, "name")
    if not text:
        return LOCATION

    context.user_data["location"] = text
    update.message.reply_text("👤 اسم المالك:")
    return OWNER

# =========================
# 👤 المالك
# =========================
def get_owner(update, context):
    text = validate(update, "name")
    if not text:
        return OWNER

    context.user_data["owner"] = text
    update.message.reply_text("📄 نوع الوثيقة:")
    return DOC_TYPE

# =========================
# 📄 الوثيقة
# =========================
def get_doc_type(update, context):
    context.user_data["doc_type"] = update.message.text
    update.message.reply_text("🔢 رقم الوثيقة:")
    return DOC_NUM

# =========================
# 🔢 الرقم
# =========================
def get_doc_num(update, context):
    text = validate(update, "doc_num")
    if not text:
        return DOC_NUM

    context.user_data["doc_num"] = text
    update.message.reply_text("📅 أدخل التاريخ:")
    return DOC_DATE

# =========================
# 📅 التاريخ (مهم جداً)
# =========================
def get_doc_date(update, context):
    text = validate(update, "date")
    if not text:
        return DOC_DATE

    context.user_data["doc_date"] = text

    update.message.reply_text(
        "📅 تم تسجيل التاريخ بنجاح\n"
        "🏛️ الآن أرسل الجهة المصدرة:"
    )
    return ISSUER

# =========================
# 🏛️ الجهة
# =========================
def get_issuer(update, context):
    context.user_data["issuer"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("شراء", callback_data="buy")],
        [InlineKeyboardButton("ورث", callback_data="inherit")]
    ]

    update.message.reply_text(
        "⚖️ نوع الحيازة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return INHERITANCE

# =========================
# ⚖️ الحيازة
# =========================
def get_inheritance(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["inheritance"] = query.data

    keyboard = [
        [InlineKeyboardButton("لا يوجد مشاكل", callback_data="no")],
        [InlineKeyboardButton("يوجد مشاكل", callback_data="yes")]
    ]

    query.edit_message_text(
        "⚠️ هل توجد مشاكل؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROBLEMS

# =========================
# 📊 التحليل
# =========================
def get_problems(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["problems"] = query.data

    inh = context.user_data["inheritance"]
    prob = context.user_data["problems"]

    # 🧠 تحليل أولي
    score = 50

    if inh == "buy":
        score += 15
    else:
        score -= 10

    if prob == "yes":
        score -= 30

    score = max(20, min(70, score))  # تحليل أولي فقط (20-70)

    if score >= 60:
        color = "🟢"
    elif score >= 40:
        color = "🟡"
    else:
        color = "🔴"

    msg = f"""
🛡️ تقرير التحليل الأولي

👤 {context.user_data['name']}
📍 {context.user_data['location']}

📊 النتيجة: {color} {score}%

⏳ النتيجة النهائية خلال 24 ساعة

📞 واتساب: 00967778160500
💬 تليجرام: https://t.me/fan_al_prompt
🌐 الموقع: https://sites.google.com/view/aldira-yemen
"""

    keyboard = [
        [InlineKeyboardButton("📱 واتساب", url="https://wa.me/967778160500")],
        [InlineKeyboardButton("💬 تليجرام", url="https://t.me/fan_al_prompt")],
        [InlineKeyboardButton("🌐 الموقع", url="https://sites.google.com/view/aldira-yemen")],
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="restart")]
    ]

    query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    # إرسال للأدمن
    if ADMIN_ID:
        context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    reset_user(context)
    return ConversationHandler.END

# =========================
# ❌ إلغاء
# =========================
def cancel(update, context):
    update.message.reply_text("❌ تم الإلغاء")
    reset_user(context)
    return ConversationHandler.END

# =========================
# 🔁 إعادة
# =========================
def restart(update, context):
    query = update.callback_query
    query.answer()

    reset_user(context)

    query.edit_message_text(
        WELCOME_MSG,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
            [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")],
            [InlineKeyboardButton("🔧 استشارة فنية", callback_data="technical")]
        ])
    )
    return SERVICE

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
            SERVICE: [CallbackQueryHandler(service_selected)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            LOCATION: [MessageHandler(Filters.text & ~Filters.command, get_location)],
            OWNER: [MessageHandler(Filters.text & ~Filters.command, get_owner)],
            DOC_TYPE: [MessageHandler(Filters.text & ~Filters.command, get_doc_type)],
            DOC_NUM: [MessageHandler(Filters.text & ~Filters.command, get_doc_num)],
            DOC_DATE: [MessageHandler(Filters.text & ~Filters.command, get_doc_date)],
            ISSUER: [MessageHandler(Filters.text & ~Filters.command, get_issuer)],
            INHERITANCE: [CallbackQueryHandler(get_inheritance)],
            PROBLEMS: [CallbackQueryHandler(get_problems)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=300
    )

    dp.add_handler(conv)
    dp.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))

    print("🛡️ نظام الدرع يعمل...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
