import os
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters
)

# --- 1. جزء إرضاء سيرفر Render (الميناء الوهمي) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# تشغيل الخادم الوهمي في خيط منفصل ليتجاوز خطأ Port timeout
threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. إعدادات البوت الأساسية ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8763108829:AAFhUup54-e6t3QsOMBfYemQusI9qpJlvTM"  # الأفضل استخدام Environment Variables
ADMIN_ID = 5068122021
DATA_FILE = "data/clients.json"

# تحميل وحفظ البيانات
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

# تعريف مراحل المحادثة
NAME, SERVICE, LOCATION, OWNER, DOC_TYPE, DOC_NUM, DOC_DATE, ISSUER, INHERITANCE, PROBLEMS = range(10)

WELCOME_MSG = """
🛡️ نظام الدرع v23 - اليمن

أهلاً بك في نظام حماية الاستثمار العقاري

📋 الخدمات:
• فحص قانوني
• تقييم مخاطر
• استشارة فنية

⚠️ النتيجة النهائية خلال 24 ساعة

🔽 اختر الخدمة:
"""

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
        [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")],
        [InlineKeyboardButton("🔧 استشارة فنية", callback_data="technical")]
    ]
    update.message.reply_text(
        WELCOME_MSG, 
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SERVICE

# باقي الدوال كما هي (get_name, get_location, إلخ) بدون تغيير...

def get_problems(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["problems"] = query.data
    
    inh = context.user_data["inheritance"]
    prob = context.user_data["problems"]
    
    if inh == "buy" and prob == "no":
        score, color, risk = 70, "🟢", "منخفض"
    elif inh == "buy" and prob == "yes":
        score, color, risk = 50, "🟡", "متوسط"
    elif inh == "inherit" and prob == "no":
        score, color, risk = 50, "🟡", "متوسط"
    else:
        score, color, risk = 20, "🔴", "عالي جداً"
    
    context.user_data.update({
        "score": score, "color": color, "risk": risk,
        "date": datetime.now().isoformat()
    })
    
    data = load_data()
    user_id = str(query.from_user.id)
    if user_id not in data:
        data[user_id] = []
    data[user_id].append(context.user_data)
    save_data(data)
    
    msg = f"""
🛡️ نظام الدرع v23 - تقرير تحليل عقاري

👤 العميل: {context.user_data['name']}
📍 الموقع: {context.user_data['location']}
👤 المالك: {context.user_data['owner']}

📋 الوثيقة:
• النوع: {context.user_data['doc_type']}
• الرقم: {context.user_data['doc_num']}
• التاريخ: {context.user_data['doc_date']}
• المصدر: {context.user_data['issuer']}

⚖️ الحيازة: {"شراء" if inh == "buy" else "ورث"}
⚠️ المشاكل: {"لا يوجد" if prob == "no" else "يوجد"}

📊 النتيجة: {color} {score}% - خطر {risk}

⏳ النتيجة النهائية خلال 24 ساعة

📞 للاستفسار: 00967778160500
📢 القناة: @fanalprompt
🌐 الموقع: aldira-yemen.com
"""
    
    keyboard = [
        [InlineKeyboardButton("📱 واتساب", url="https://wa.me/967778160500")],
        [InlineKeyboardButton("💬 تليجرام", url="https://t.me/fanalprompt")],
        [InlineKeyboardButton("🌐 الموقع", url="https://aldira-yemen.com")],
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="restart")]
    ]
    
    query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    if ADMIN_ID:
        admin_msg = f"🔔 طلب جديد!\nمن: {context.user_data['name']}\nالنسبة: {score}% {color}"
        try:
            context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        except:
            pass
    
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
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
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    
    print("🛡️ نظام الدرع يعمل...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
