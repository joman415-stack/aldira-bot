# bot.py - نظام الدرع v23
import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, ContextTypes, filters

# التوكن من متغيرات Railway
TOKEN = os.getenv("8763108829:AAGSyWX_sspwTZMM5G_E8y1QvyDLhZkV_9Q")

ADMIN_ID = os.getenv("ADMIN_ID = 5068122021")
  # رقمك أنت كمشرف
# حفظ البيانات في ملف JSON
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

# مراحل المحادثة
(START, NAME, SERVICE, LOCATION, OWNER, DOC_TYPE, DOC_NUM, DOC_DATE, 
 ISSUER, INHERITANCE, PROBLEMS, ANALYZE) = range(12)

# الرسالة التركيبية
WELCOME_MSG = """
🛡️ *نظام الدرع v23 - اليمن*

أهلاً بك في نظام حماية الاستثمار العقاري

📋 *الخدمات المتوفرة:*
• فحص قانوني شامل
• تقييم مخاطر الاستثمار
• استشارة فنية

⚠️ *تنبيه:* النتيجة الأولية آلية، والنهائية خلال 24 ساعة من خبير

🔽 اختر الخدمة المطلوبة:
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏠 فحص قانوني", callback_data="legal")],
        [InlineKeyboardButton("📊 تقييم مخاطر", callback_data="risk")],
        [InlineKeyboardButton("🔧 استشارة فنية", callback_data="technical")]
    ]
    await update.message.reply_text(WELCOME_MSG, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SERVICE

async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = query.data
    
    await query.edit_message_text("✏️ أرسل اسمك الكامل:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📍 المحافظة:")
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text
    await update.message.reply_text("👤 اسم المالك:")
    return OWNER

async def get_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["owner"] = update.message.text
    await update.message.reply_text("📄 نوع الوثيقة (عقد/حجة/قرار/أخرى):")
    return DOC_TYPE

async def get_doc_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["doc_type"] = update.message.text
    await update.message.reply_text("🔢 رقم الوثيقة:")
    return DOC_NUM

async def get_doc_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["doc_num"] = update.message.text
    await update.message.reply_text("📅 تاريخ إصدار الوثيقة:")
    return DOC_DATE

async def get_doc_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["doc_date"] = update.message.text
    await update.message.reply_text("🏛️ الجهة المصدرة:")
    return ISSUER

async def get_issuer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["issuer"] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("🛒 شراء", callback_data="buy")],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 ورث", callback_data="inherit")]
    ]
    await update.message.reply_text("نوع الحيازة:", reply_markup=InlineKeyboardMarkup(keyboard))
    return INHERITANCE

async def get_inheritance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["inheritance"] = query.data
    
    keyboard = [
        [InlineKeyboardButton("✅ لا يوجد", callback_data="no")],
        [InlineKeyboardButton("❌ يوجد", callback_data="yes")]
    ]
    await query.edit_message_text("هل يوجد نزاعات/مشاكل على العقار؟", reply_markup=InlineKeyboardMarkup(keyboard))
    return PROBLEMS

async def get_problems(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["problems"] = query.data
    
    # حساب النسبة
    inh = context.user_data["inheritance"]
    prob = context.user_data["problems"]
    
    if inh == "buy" and prob == "no":
        score = 70
        color = "🟢"
        risk = "منخفض"
    elif inh == "buy" and prob == "yes":
        score = 50
        color = "🟡"
        risk = "متوسط"
    elif inh == "inherit" and prob == "no":
        score = 50
        color = "🟡"
        risk = "متوسط"
    else:  # inherit + yes
        score = 20
        color = "🔴"
        risk = "عالي جداً"
    
    context.user_data["score"] = score
    context.user_data["color"] = color
    context.user_data["risk"] = risk
    context.user_data["date"] = datetime.now().isoformat()
    context.user_data["chat_id"] = query.message.chat_id
    
    # حفظ البيانات
    data = load_data()
    user_id = str(query.from_user.id)
    if user_id not in data:
        data[user_id] = []
    data[user_id].append(context.user_data)
    save_data(data)
    
    # الرسالة التركيبية النهائية
    msg = f"""
🛡️ *نظام الدرع v23 - تقرير تحليل عقاري*

👤 *العميل:* {context.user_data['name']}

📍 *الموقع:* {context.user_data['location']}
👤 *المالك:* {context.user_data['owner']}

📋 *الوثيقة:*
• النوع: {context.user_data['doc_type']}
• الرقم: {context.user_data['doc_num']}
• التاريخ: {context.user_data['doc_date']}
• المصدر: {context.user_data['issuer']}

⚖️ *الحيازة:* {"شراء" if inh == "buy" else "ورث"}
⚠️ *المشاكل:* {"لا يوجد" if prob == "no" else "يوجد"}

📊 *نتيجة التحليل الأولي:*
{color} *{score}%* - خطر {risk}

⏳ *النتيجة النهائية خلال 24 ساعة*
👨‍⚖️ تحليل خبير قانوني وفني

📞 *للاستفسار العاجل:*
00967778160500

📢 *قناة الدرع:* @fan_al_prompt
🌐 *الموقع:* aldira-yemen.com
"""
    
    # أزرار التواصل
    keyboard = [
        [InlineKeyboardButton("📱 واتساب", url="https://wa.me/967778160500")],
        [InlineKeyboardButton("💬 تليجرام", url="https://t.me/fan_al_prompt")],
        [InlineKeyboardButton("🌐 الموقع", url="https://sites.google.com/view/aldira-yemen")],
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="restart")]
    ]
    
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # إشعار للأدمن
    if ADMIN_ID:
        admin_msg = f"""
🔔 *طلب جديد في الدرع!*

من: {context.user_data['name']}
المحافظة: {context.user_data['location']}
النسبة: {score}% {color}

الرقم: {context.user_data.get('doc_num', 'غير متوفر')}
"""
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
        except:
            pass
    
    return ConversationHandler.END

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)
    return SERVICE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم الإلغاء. أرسل /start للبدء من جديد")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SERVICE: [CallbackQueryHandler(service_selected)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            OWNER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_owner)],
            DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_doc_type)],
            DOC_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_doc_num)],
            DOC_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_doc_date)],
            ISSUER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_issuer)],
            INHERITANCE: [CallbackQueryHandler(get_inheritance)],
            PROBLEMS: [CallbackQueryHandler(get_problems)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    
    application.run_polling()

if __name__ == "__main__":
    main()
