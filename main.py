"""
🚀 بوت "عِلم" - النسخة المتكاملة
--------------------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import logging
import sqlite3
from flask import Flask, request, jsonify
import requests

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# المتغيرات
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE', '771267')
COLLEGE_NAME = os.getenv('COLLEGE_NAME', 'كلية الحاسبات وتقنية المعلومات')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN غير موجود!")
    exit(1)

# إنشاء Flask
app = Flask(__name__)

# ====== قاعدة البيانات ======
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS professors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, year TEXT, term TEXT, subject TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prof_id INTEGER, type TEXT, title TEXT, url TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY, name TEXT, points INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()

init_db()

# ====== الإعدادات ======
DEVELOPER_NAME = "أحمد حمدي أحمد عثمان المقطري"
CONTACT_NUMBERS = ["771267564", "738805009"]

WELCOME_MESSAGE = f"""🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *الميزات:*
• 🔢 حل المعادلات الرياضية
• 👨‍🏫 البحث عن الدكاترة والمواد
• 📸 قراءة الصور (OCR)
• 🧠 الرد الذكي
• 🎓 التنقل بين السنوات والترمات

🎯 *اختر السنة الدراسية:*
"""

# ====== دالة إرسال الرسائل ======
def send_msg(chat_id, text, buttons=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")

# ====== الأزرار الرئيسية ======
def get_years_buttons():
    return [
        [{"text": "📚 السنة الأولى", "callback_data": "year:1"}],
        [{"text": "📚 السنة الثانية", "callback_data": "year:2"}],
        [{"text": "📚 السنة الثالثة", "callback_data": "year:3"}],
        [{"text": "📚 السنة الرابعة", "callback_data": "year:4"}],
        [{"text": "🔢 آلة حاسبة", "callback_data": "calc"}],
        [{"text": "📸 حل من صورة", "callback_data": "ocr"}],
        [{"text": "👨‍🏫 البحث عن دكتور", "callback_data": "search"}],
        [{"text": "👑 لوحة المدير", "callback_data": "admin"}]
    ]

def get_terms_buttons(year):
    return [
        [{"text": "📖 الترم الأول", "callback_data": f"term:{year}:1"}],
        [{"text": "📖 الترم الثاني", "callback_data": f"term:{year}:2"}],
        [{"text": "🔙 رجوع", "callback_data": "back:years"}]
    ]

# ====== Webhook ======
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
                send_msg(chat_id, WELCOME_MESSAGE, get_years_buttons())
            
            elif text == "/help":
                send_msg(chat_id, "🆘 *المساعدة*\n\n/start - الرئيسية\n/calc - آلة حاسبة\n/admin - لوحة المدير")
            
            elif text == "/calc":
                send_msg(chat_id, "🔢 *آلة حاسبة*\n\nأرسل المعادلة مثل:\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`")
            
            elif text == "/admin":
                send_msg(chat_id, "👑 *لوحة تحكم المدير*\n\n🔐 أرسل رمز الدخول:")
            
            elif text.startswith("/calc "):
                # حل المعادلة
                try:
                    expr = text[6:]
                    # هنا نضيف حل المعادلات لاحقاً
                    send_msg(chat_id, f"🔢 *المعادلة:* `{expr}`\n\n⏳ جاري الحل...")
                except:
                    send_msg(chat_id, "❌ خطأ في المعادلة")
            
            else:
                # البحث الذكي
                send_msg(chat_id, f"🤔 *بحث عن:* `{text}`\n\nجاري البحث في الدكاترة...", [
                    [{"text": "🔍 بحث متقدم", "callback_data": f"search:{text}"}]
                ])
        
        # معالجة الأزرار (Callback)
        elif "callback_query" in data:
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            msg_id = data["callback_query"]["message"]["message_id"]
            callback = data["callback_query"]["data"]
            
            if callback.startswith("year:"):
                year = callback.split(":")[1]
                year_names = {"1": "الأولى", "2": "الثانية", "3": "الثالثة", "4": "الرابعة"}
                send_msg(chat_id, f"📚 *السنة {year_names.get(year, year)}*\n\nاختر الترم:", get_terms_buttons(year))
            
            elif callback.startswith("term:"):
                parts = callback.split(":")
                year, term = parts[1], parts[2]
                send_msg(chat_id, f"👨‍🏫 *دكاترة السنة {year} - الترم {term}*\n\n⚠️ لا يوجد دكاترة مسجلين بعد.\n\nيمكنك إضافتهم من لوحة التحكم.", [
                    [{"text": "➕ إضافة دكتور", "callback_data": f"add_prof:{year}:{term}"}],
                    [{"text": "🔙 رجوع", "callback_data": f"back:year:{year}"}]
                ])
            
            elif callback == "calc":
                send_msg(chat_id, "🔢 *آلة حاسبة*\n\nأرسل المعادلة:\n\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`\n`diff(x**2, x)` - مشتقة\n`integrate(x, x)` - تكامل")
            
            elif callback == "ocr":
                send_msg(chat_id, "📸 *OCR - قراءة الصور*\n\nأرسل صورة معادلة وسأقرأها وأحلها!\n\n⚠️ تأكد أن الصورة واضحة.")
            
            elif callback == "search":
                send_msg(chat_id, "🔍 *البحث عن دكتور*\n\nاكتب اسم الدكتور أو المادة:")
            
            elif callback == "admin":
                send_msg(chat_id, "👑 *لوحة تحكم المدير*\n\n🔐 أرسل رمز الدخول (4 أرقام):")
            
            elif callback.startswith("back:"):
                if callback == "back:years":
                    send_msg(chat_id, WELCOME_MESSAGE, get_years_buttons())
        
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return jsonify({'ok': False, 'error': str(e)})

# ====== تشغيل ======
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=PORT)
