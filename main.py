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

# --- 🔥 0. التوكن ---
TOKEN = "8763108829:AAGl10eR5hGJCnBgkF2v2lCWY7Ut7hWurnc"
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود")

ADMIN_ID = 5068122021
DATA_FILE = "data/clients.json"

# --- 1. سيرفر Render ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. logging ---
logging.basicConfig(level=logging.INFO)

def error_handler(update, context):
    logging.error("خطأ:", exc_info=context.error)

# --- 3. Validation ---
def validate_input(update, field_type):
    text = update.message.text.strip()

    if not text:
        update.message.reply_text("⚠️ لا يمكن ترك الحقل فارغ.")
        return None

    if field_type == "name":
        if len(text) < 3:
            update.message.reply_text("⚠️ الاسم قصير جداً.")
            return None
        if not re.match(r"^[\u0600-\u06FF\s]+$", text):
            update.message.reply_text("⚠️ أدخل اسم عربي صحيح.")
            return None

    elif field_type == "location":
        if len(text) < 2:
            update.message.reply_text("⚠️ الموقع غير صحيح.")
            return None

    elif field_type == "doc_num":
        if not text.isdigit():
            update.message.reply_text("⚠️ رقم الوثيقة يجب أن يكون أرقام فقط.")
            return None

    elif field_type == "date":
        try:
            datetime.strptime(text, "%Y-%m-%d")
        except:
            update.message.reply_text("⚠️ استخدم الصيغة YYYY-MM-DD")
            return None

    return text

# --- 4. data ---
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

# --- 5. states ---
NAME, SERVICE, LOCATION, OWNER, DOC_TYPE, DOC_NUM, DOC_DATE, ISSUER, INHERITANCE, PROBLEMS = range(10)

WELCOME_MSG = """
🛡️ نظام الدرع v23 - اليمن

أهلاً بك في نظام حماية الاستثمار العقاري

🔽 اختر الخدمة:
"""

def reset_user_data(context):
    context.user_data.clear()

# --- 6. handlers ---
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
        [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")],
        [InlineKeyboardButton("🔧 استشارة فنية", callback_data="technical")]
    ]
    update.message.reply_text(WELCOME_MSG, reply_markup=InlineKeyboardMarkup(keyboard))
    return SERVICE

def service_selected(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["service"] = query.data
    query.edit_message_text("✏️ أرسل اسمك الكامل:")
    return NAME

def get_name(update, context):
    text = validate_input(update, "name")
    if not text:
        return NAME

    context.user_data["name"] = text
    update.message.reply_text("📍 المحافظة:")
    return LOCATION

def get_location(update, context):
    text = validate_input(update, "location")
    if not text:
        return LOCATION

    context.user_data["location"] = text
    update.message.reply_text("👤 اسم المالك:")
    return OWNER

def get_owner(update, context):
    text = validate_input(update, "name")
    if not text:
        return OWNER

    context.user_data["owner"] = text
    update.message.reply_text("📄 نوع الوثيقة:")
    return DOC_TYPE

def get_doc_type(update, context):
    text = validate_input(update, "name")
    if not text:
        return DOC_TYPE

    context.user_data["doc_type"] = text
    update.message.reply_text("🔢 رقم الوثيقة:")
    return DOC_NUM

def get_doc_num(update, context):
    text = validate_input(update, "doc_num")
    if not text:
        return DOC_NUM

    context.user_data["doc_num"] = text
    update.message.reply_text("📅 أدخل التاريخ:")
    return DOC_DATE

# 🔥 التعديل هنا فقط (تحسين الرسالة)
def get_doc_date(update, context):
    text = validate_input(update, "date")
    if not text:
        return DOC_DATE

    context.user_data["doc_date"] = text

    update.message.reply_text(
        "📅 أدخل تاريخ الإصدار:\n"
        "✳️ الصيغة المطلوبة: YYYY-MM-DD\n"
        "📌 مثال: 2026-04-19\n\n"
        "⚠️ تأكد أن التاريخ صحيح بدون أخطاء"
    )

    return ISSUER

def get_issuer(update, context):
    text = validate_input(update, "name")
    if not text:
        return ISSUER

    context.user_data["issuer"] = text

    keyboard = [
        [InlineKeyboardButton("شراء", callback_data="buy")],
        [InlineKeyboardButton("ورث", callback_data="inherit")]
    ]

    update.message.reply_text("⚖️ نوع الحيازة:", reply_markup=InlineKeyboardMarkup(keyboard))
    return INHERITANCE

def get_inheritance(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["inheritance"] = query.data

    keyboard = [
        [InlineKeyboardButton("لا يوجد مشاكل", callback_data="no")],
        [InlineKeyboardButton("يوجد مشاكل", callback_data="yes")]
    ]

    query.edit_message_text("⚠️ هل توجد مشاكل؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return PROBLEMS

def get_problems(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["problems"] = query.data

    inh = context.user_data.get("inheritance")

    score = 50
    if inh == "buy":
        score += 10
    if context.user_data["problems"] == "yes":
        score -= 30

    score = max(0, min(100, score))

    color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

    msg = f"""
🛡️ تقرير الدرع

👤 {context.user_data['name']}
📍 {context.user_data['location']}
📊 {color} {score}%
"""

    query.edit_message_text(msg)

    data = load_data()
    uid = str(query.from_user.id)

    if uid not in data:
        data[uid] = []

    data[uid].append(dict(context.user_data))
    save_data(data)

    if ADMIN_ID:
        context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    reset_user_data(context)
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("❌ تم الإلغاء")
    reset_user_data(context)
    return ConversationHandler.END

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

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
