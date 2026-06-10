"""
🚀 بوت "عِلم" - النسخة النهائية
--------------------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import logging
from flask import Flask, request, jsonify
import requests

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

# ====== دالة إرسال الرسائل ======
def send_message(chat_id, text):
    """إرسال رسالة عبر Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال: {e}")

# ====== Webhook Endpoint ======
@app.route('/')
def home():
    return "🚀 بوت عِلم يعمل!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            
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

