"""
🎓 بوت "عِلم" - للطلاب
----------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import logging
import sqlite3
from flask import Flask, request, jsonify
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8724867533:AAE4mVFqmv8CA_FhVaxkdgUvnx4_Nuhk1uI"
COLLEGE_NAME = "كلية الحاسبات وتقنية المعلومات"

app = Flask(__name__)

def send_msg(chat_id, text, buttons=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")

# ====== التصميم الاحترافي ======
def get_main_buttons():
    """الأزرار الرئيسية - تصميم مستويات"""
    return [
        [{"text": "🎓 مستوى أول 1️⃣\nFIRST LEVEL", "callback_data": "year:1"}],
        [{"text": "🎓 مستوى ثاني 2️⃣\nSECOND LEVEL", "callback_data": "year:2"}],
        [{"text": "🎓 مستوى ثالث 3️⃣\nTHIRD LEVEL", "callback_data": "year:3"}],
        [{"text": "🎓 مستوى رابع 4️⃣\nFOURTH LEVEL", "callback_data": "year:4"}],
        [{"text": "📋 الخطة الدراسية", "callback_data": "plan"}],
        [{"text": "🔢 آلة حاسبة ذكية", "callback_data": "calc"}],
        [{"text": "📸 OCR - قراءة الصور", "callback_data": "ocr"}],
        [{"text": "👨‍🏫 البحث عن دكتور", "callback_data": "search"}]
    ]

def get_terms_buttons(year):
    return [
        [{"text": "📖 الترم الأول", "callback_data": f"term:{year}:1"}],
        [{"text": "📖 الترم الثاني", "callback_data": f"term:{year}:2"}],
        [{"text": "🔙 رجوع للمستويات", "callback_data": "back:main"}]
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

🏛️ *{COLLEGE_NAME}*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *ما يمكنك فعله:*
• 🎓 التنقل بين المستويات الدراسية
• 👨‍🏫 البحث عن الدكاترة والمواد
• 🔗 الانضمام للمجموعات والقنوات
• 📱 تحميل التطبيقات المفيدة
• 🔢 حل المعادلات الرياضية
• 📸 قراءة المعادلات من الصور

🎯 *اختر المستوى الدراسي:*""", get_main_buttons())
            
            # ✅ البحث العادي
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
                        response += f"📚 *{name}*\nالمستوى: {year} | الترم: {term}\nالمادة: {subject}\n\n"
                    send_msg(chat_id, response)
                else:
                    send_msg(chat_id, f"""🤔 *لم أجد نتائج للبحث:* `{text}`

🔧 *الذكاء الاصطناعي يقترح:*
• التأكد من إملاء الاسم
• البحث باسم المادة
• التنقل بين المستويات

🎯 *للبدء:* /start""", get_main_buttons())
        
        # ====== الأزرار ======
        elif "callback_query" in data:
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            callback = data["callback_query"]["data"]
            
            if callback.startswith("year:"):
                year = callback.split(":")[1]
                year_names = {"1": "الأول", "2": "الثاني", "3": "الثالث", "4": "الرابع"}
                send_msg(chat_id, f"""🎓 *المستوى {year_names.get(year, year)}*

📚 *اختر الترم الدراسي:*""", get_terms_buttons(year))
            
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
                
                response = f"""🎓 *المستوى {year} - الترم {term_names.get(term, term)}*

👨‍🏫 *الدكاترة:*\n"""
                
                if professors:
                    for prof in professors:
                        prof_id, name, y, t, subject, created = prof
                        response += f"• 📚 *{name}* - {subject}\n"
                else:
                    response += "⚠️ لا يوجد دكاترة مسجلين\n"
                
                if groups:
                    response += f"\n🔗 *المجموعات:*\n"
                    for group in groups:
                        group_id, name, y, t, subject, link, g_type, created = group
                        response += f"• [{name}]({link})\n"
                
                send_msg(chat_id, response, [
                    [{"text": "🔙 رجوع للمستويات", "callback_data": "back:main"}]
                ])
            
            elif callback == "plan":
                send_msg(chat_id, f"""📋 *الخطة الدراسية*

🏛️ *{COLLEGE_NAME}*

🎓 *المستوى الأول:*
• رياضيات 1
• فيزياء 1
• برمجة 1

🎓 *المستوى الثاني:*
• رياضيات 2
• فيزياء 2
• برمجة 2

🎓 *المستوى الثالث:*
• ذكاء اصطناعي
• قواعد بيانات
• شبكات

🎓 *المستوى الرابع:*
• مشروع تخرج
• تدريب عملي""", [
                    [{"text": "🔙 رجوع", "callback_data": "back:main"}]
                ])
            
            elif callback == "calc":
                send_msg(chat_id, """🔢 *آلة حاسبة ذكية*

📝 *أمثلة على المعادلات:*
• `2*x + 3 = 7`
• `x**2 + 5*x - 6`
• `diff(x**2, x)` - مشتقة
• `integrate(x, x)` - تكامل

✨ *أرسل معادلتك الآن:*""")
            
            elif callback == "ocr":
                send_msg(chat_id, """📸 *OCR - قراءة الصور*

📝 *أرسل صورة معادلة وسأقرأها وأحلها!*

🔧 *نصائح للحصول على أفضل نتيجة:*
• الصورة واضحة وغير مظلمة
• الخلفية فاتحة اللون
• المعادلة مرئية بوضوح
• تجنب الظلال والانعكاسات""")
            
            elif callback == "search":
                send_msg(chat_id, """🔍 *البحث الذكي*

📝 *اكتب اسم الدكتور أو المادة:*

✨ *أمثلة:*
• "دكتور أحمد"
• "رياضيات"
• "برمجة"""")
            
            elif callback == "back:main":
                send_msg(chat_id, f"""🎓 *مرحباً بك في بوت "عِلم"*

🏛️ *{COLLEGE_NAME}*

🎯 *اختر المستوى الدراسي:*""", get_main_buttons())
        
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return jsonify({'ok': False, 'error': str(e)})

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '10000'))
    app.run(host='0.0.0.0', port=PORT)
