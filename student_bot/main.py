"""
🎓 بوت "عِلم - الطلاب" - للجميع
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
BOT_TOKEN = "8724867533:AAE4mVFqmv8CA_FhVaxkdgUvnx4_Nuhk1uI"
COLLEGE_NAME = "كلية الحاسبات وتقنية المعلومات"

# إنشاء Flask
app = Flask(__name__)

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

# ====== الأزرار ======
def get_years_buttons():
    return [
        [{"text": "📚 السنة الأولى", "callback_data": "year:1"}],
        [{"text": "📚 السنة الثانية", "callback_data": "year:2"}],
        [{"text": "📚 السنة الثالثة", "callback_data": "year:3"}],
        [{"text": "📚 السنة الرابعة", "callback_data": "year:4"}],
        [{"text": "🔗 المجموعات", "callback_data": "groups"}],
        [{"text": "📢 القنوات", "callback_data": "channels"}],
        [{"text": "📱 التطبيقات", "callback_data": "apps"}],
        [{"text": "🔢 آلة حاسبة", "callback_data": "calc"}]
    ]

def get_terms_buttons(year):
    return [
        [{"text": "📖 الترم الأول", "callback_data": f"term:{year}:1"}],
        [{"text": "📖 الترم الثاني", "callback_data": f"term:{year}:2"}],
        [{"text": "🔙 رجوع للسنوات", "callback_data": "back:years"}]
    ]

# ====== Webhook ======
@app.route('/')
def home():
    return "🎓 بوت عِلم - للطلاب"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            
            # ✅ /start
            if text == "/start":
                send_msg(chat_id, f"""🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *ما يمكنك فعله:*
• 📚 التنقل بين السنوات والترمات
• 👨‍🏫 البحث عن الدكاترة والمواد
• 🔗 الانضمام للمجموعات
• 📢 متابعة القنوات
• 📱 تحميل التطبيقات
• 🔢 آلة حاسبة

🎯 *اختر ما تريد:*""", get_years_buttons())
            
            # ✅ البحث عن دكتور
            else:
                conn = sqlite3.connect('../database.db')
                c = conn.cursor()
                c.execute('SELECT * FROM professors WHERE name LIKE ?', (f'%{text}%',))
                professors = c.fetchall()
                conn.close()
                
                if professors:
                    response = f"👨‍🏫 *نتائج البحث:*\n\n"
                    for prof in professors:
                        prof_id, name, year, term, subject, created = prof
                        response += f"📚 *{name}*\nالسنة: {year} | الترم: {term}\nالمادة: {subject}\n\n"
                    send_msg(chat_id, response)
                else:
                    send_msg(chat_id, f"🤔 *لم أجد نتائج للبحث:* `{text}`\n\nجرب:\n• كتابة اسم دكتور آخر\n• /start للتنقل بين السنوات")
        
        # ====== معالجة الأزرار ======
        elif "callback_query" in data:
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            callback = data["callback_query"]["data"]
            
            if callback.startswith("year:"):
                year = callback.split(":")[1]
                year_names = {"1": "الأولى", "2": "الثانية", "3": "الثالثة", "4": "الرابعة"}
                send_msg(chat_id, f"📚 *السنة {year_names.get(year, year)}*\n\nاختر الترم:", get_terms_buttons(year))
            
            elif callback.startswith("term:"):
                parts = callback.split(":")
                year, term = parts[1], parts[2]
                term_names = {"1": "الأول", "2": "الثاني"}
                
                conn = sqlite3.connect('../database.db')
                c = conn.cursor()
                c.execute('SELECT * FROM professors WHERE year = ? AND term = ?', (year, term))
                professors = c.fetchall()
                c.execute('SELECT * FROM groups WHERE year = ? AND term = ?', (year, term))
                groups = c.fetchall()
                conn.close()
                
                response = f"👨‍🏫 *دكاترة السنة {year} - الترم {term_names.get(term, term)}*\n\n"
                
                if professors:
                    for prof in professors:
                        prof_id, name, y, t, subject, created = prof
                        response += f"• *{name}* - {subject}\n"
                else:
                    response += "⚠️ لا يوجد دكاترة مسجلين\n"
                
                if groups:
                    response += f"\n🔗 *المجموعات:*\n"
                    for group in groups:
                        group_id, name, y, t, subject, link, g_type, created = group
                        response += f"• [{name}]({link})\n"
                
                send_msg(chat_id, response, [
                    [{"text": "🔙 رجوع", "callback_data": f"back:year:{year}"}]
                ])
            
            elif callback == "groups":
                conn = sqlite3.connect('../database.db')
                c = conn.cursor()
                c.execute('SELECT * FROM groups')
                groups = c.fetchall()
                conn.close()
                
                if groups:
                    response = "🔗 *المجموعات المتاحة:*\n\n"
                    for group in groups:
                        group_id, name, year, term, subject, link, g_type, created = group
                        response += f"• [{name}]({link})\nالسنة: {year} | الترم: {term}\n\n"
                    send_msg(chat_id, response)
                else:
                    send_msg(chat_id, "⚠️ *لا توجد مجموعات مسجلة*\n\nسيتم إضافتها قريباً!")
            
            elif callback == "channels":
                conn = sqlite3.connect('../database.db')
                c = conn.cursor()
                c.execute('SELECT * FROM channels')
                channels = c.fetchall()
                conn.close()
                
                if channels:
                    response = "📢 *القنوات المتاحة:*\n\n"
                    for channel in channels:
                        channel_id, name, link, description, created = channel
                        response += f"• [{name}]({link})\n{description}\n\n"
                    send_msg(chat_id, response)
                else:
                    send_msg(chat_id, "⚠️ *لا توجد قنوات مسجلة*\n\nسيتم إضافتها قريباً!")
            
            elif callback == "apps":
                conn = sqlite3.connect('../database.db')
                c = conn.cursor()
                c.execute('SELECT * FROM apps')
                apps = c.fetchall()
                conn.close()
                
                if apps:
                    response = "📱 *التطبيقات المتاحة:*\n\n"
                    for app in apps:
                        app_id, name, link, description, created = app
                        response += f"• [{name}]({link})\n{description}\n\n"
                    send_msg(chat_id, response)
                else:
                    send_msg(chat_id, "⚠️ *لا توجد تطبيقات مسجلة*\n\nسيتم إضافتها قريباً!")
            
            elif callback == "calc":
                send_msg(chat_id, "🔢 *آلة حاسبة*\n\nأرسل المعادلة:\n\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`")
            
            elif callback.startswith("back:"):
                if callback == "back:years":
                    send_msg(chat_id, f"""🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

🎯 *اختر ما تريد:*""", get_years_buttons())
                elif callback.startswith("back:year:"):
                    year = callback.split(":")[2]
                    year_names = {"1": "الأولى", "2": "الثانية", "3": "الثالثة", "4": "الرابعة"}
                    send_msg(chat_id, f"📚 *السنة {year_names.get(year, year)}*\n\nاختر الترم:", get_terms_buttons(year))
        
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return jsonify({'ok': False, 'error': str(e)})

# ====== تشغيل ======
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=PORT)
