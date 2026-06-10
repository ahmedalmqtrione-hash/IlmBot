"""
🚀 بوت "عِلم" - النسخة النهائية بدون asyncio
-----------------------------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import logging
import threading
from flask import Flask, request, jsonify
from telegram import Bot, Update

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

# ====== دالة إرسال الرسائل في thread منفصل ======
def send_message_thread(chat_id, text):
    """إرسال رسالة في thread منفصل"""
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال: {e}")

def send_message(chat_id, text):
    """إرسال رسالة بشكل متزامن"""
    thread = threading.Thread(target=send_message_thread, args=(chat_id, text))
    thread.start()

# ====== Webhook Endpoint ======
@app.route('/')
def home():
    return "🚀 بوت عِلم يعمل!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        
        if update.message:
            chat_id = update.message.chat_id
            text = update.message.text or ""
            
            if text == "/start":
                send_message(chat_id, WELCOME_MESSAGE)
            elif text == "/help":
                send_message(chat_id, "🆘 *المساعدة*\n\nجرب: /start")
            elif text == "/calc":
                send_message(chat_id, "🔢 *آلة حاسبة*\n\nأرسل المعادلة:")
            else:
                send_message(chat_id, f"🤔 فهمتك: {text}\n\nجرب /start")
        
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return jsonify({'ok': False, 'error': str(e)})

# ====== تشغيل ======
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=PORT)
