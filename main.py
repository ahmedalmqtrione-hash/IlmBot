"""
🚀 بوت "عِلم" - النسخة النهائية
--------------------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import logging
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# المتغيرات
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
COLLEGE_NAME = os.getenv('COLLEGE_NAME', 'كلية الحاسبات')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN غير موجود!")
    exit(1)

# إنشاء Flask
app = Flask(__name__)

# إنشاء البوت
bot = Bot(token=BOT_TOKEN)

# إنشاء Dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

# ====== الإعدادات ======
DEVELOPER_NAME = "أحمد حمدي أحمد عثمان المقطري"
CONTACT_NUMBERS = ["771267564", "738805009"]

WELCOME_MESSAGE = f"""
🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *ما يمكنني فعله:*
• 🔢 حل المعادلات الرياضية
• 👨‍🏫 البحث عن الدكاترة
• 📸 قراءة الصور (OCR)
• 🧠 الرد الذكي

🎯 *ابدأ رحلتك:*
اضغط /start

─────────────────
👨‍💻 *المطور:* {DEVELOPER_NAME}
📞 *{', '.join(CONTACT_NUMBERS)}*
🏛️ *{COLLEGE_NAME}*
"""

# ====== دوال المعالجة ======
def start_handler(update, context):
    keyboard = [
        [InlineKeyboardButton("📚 السنة الأولى", callback_data="year:1")],
        [InlineKeyboardButton("📚 السنة الثانية", callback_data="year:2")],
        [InlineKeyboardButton("🔢 آلة حاسبة", callback_data="calc")],
        [InlineKeyboardButton("📸 حل من صورة", callback_data="ocr")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown', reply_markup=reply_markup)

def help_handler(update, context):
    update.message.reply_text("🆘 *المساعدة*\n\nجرب: /start", parse_mode='Markdown')

def calc_handler(update, context):
    update.message.reply_text("🔢 *آلة حاسبة*\n\nأرسل المعادلة:", parse_mode='Markdown')

def text_handler(update, context):
    text = update.message.text
    update.message.reply_text(f"🤔 فهمتك: {text}\n\nجرب /start", parse_mode='Markdown')

# ====== تسجيل المعالجات ======
dispatcher.add_handler(CommandHandler("start", start_handler))
dispatcher.add_handler(CommandHandler("help", help_handler))
dispatcher.add_handler(CommandHandler("calc", calc_handler))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# ====== Webhook Endpoint ======
@app.route('/')
def home():
    return "🚀 بوت عِلم يعمل!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return jsonify({'ok': True})

# ====== تشغيل ======
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=PORT)

