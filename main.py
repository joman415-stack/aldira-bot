import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters,
)

TOKEN = "8763108829:AAFhUup54-e6t3QsOMBfYemQusI9qpJlvTM" # ضع التوكن في Environment Variables داخل Render
ADMIN_ID = 5068122021
DATA_FILE = "data/clients.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

def service_selected(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["service"] = query.data
    query.edit_message_text("✏️ أرسل اسمك الكامل:")
    return NAME

def get_name(update, context):
    context.user_data["name"] = update.message.text
    update.message.reply_text("📍 المحافظة:")
    return LOCATION

def get_location(update, context):
    context.user_data["location"] = update.message.text
    update.message.reply_text("👤 اسم المالك:")
    return OWNER

def get_owner(update, context):
    context.user_data["owner"] = update.message.text
    update.message.reply_text("📄 نوع الوثيقة (عقد/حجة/قرار):")
    return DOC_TYPE

def get_doc_type(update, context):
    context.user_data["doc_type"] = update.message.text
    update.message.reply_text("🔢 رقم الوثيقة:")
    return DOC_NUM

def get_doc_num(update, context):
    context.user_data["doc_num"] = update.message.text
    update.message.reply_text("📅 تاريخ الإصدار:")
    return DOC_DATE

def get_doc_date(update, context):
    context.user_data["doc_date"] = update.message.text
    update.message.reply_text("🏛️ الجهة المصدرة:")
    return ISSUER

def get_issuer(update, context):
    context.user_data["issuer"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🛒 شراء", callback_data="buy")],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 ورث", callback_data="inherit")]
    ]
    update.message.reply_text("نوع الحيازة:", reply_markup=InlineKeyboardMarkup(keyboard))
    return INHERITANCE

def get_inheritance(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["inheritance"] = query.data
    keyboard = [
        [InlineKeyboardButton("✅ لا يوجد", callback_data="no")],
        [InlineKeyboardButton("❌ يوجد", callback_data="yes")]
    ]
    query.edit_message_text("هل يوجد نزاعات/مشاكل؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return PROBLEMS

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
        "date": datetime.now().isoformat(),
        "chat_id": query.message.chat.id
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
📢 القناة: @fan_al_prompt
🌐 الموقع: aldira-yemen.com
"""
    
    keyboard = [
        [InlineKeyboardButton("📱 واتساب", url="https://wa.me/967778160500")],
        [InlineKeyboardButton("💬 تليجرام", url="https://t.me/fan_al_prompt")],
        [InlineKeyboardButton("🌐 الموقع", url="https://sites.google.com/view/aldira-yemen")],
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="restart")]
    ]
    
    query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    if ADMIN_ID:
        admin_msg = f"""🔔 طلب جديد!
من: {context.user_data['name']}
المحافظة: {context.user_data['location']}
النسبة: {score}% {color}"""
        try:
            context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
        except:
            pass
    
    return ConversationHandler.END

def restart(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
        [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")],
        [InlineKeyboardButton("🔧 استشارة فنية", callback_data="technical")]
    ]
    query.edit_message_text(WELCOME_MSG, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SERVICE

def cancel(update, context):
    update.message.reply_text("❌ تم الإلغاء. أرسل /start للبدء")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SERVICE: [CallbackQueryHandler(service_selected)],
            NAME: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_name)],
            LOCATION: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_location)],
            OWNER: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_owner)],
            DOC_TYPE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_doc_type)],
            DOC_NUM: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_doc_num)],
            DOC_DATE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_doc_date)],
            ISSUER: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, get_issuer)],
            INHERITANCE: [CallbackQueryHandler(get_inheritance)],
            PROBLEMS: [CallbackQueryHandler(get_problems)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    
    print("🛡️ نظام الدرع v23 يعمل...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
