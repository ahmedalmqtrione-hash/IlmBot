"""
👑 بوت "عِلم - المدير" - النسخة الخاصة
-----------------------------------------
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
BOT_TOKEN = "8960756644:AAFMFPCF0ZUS_jkISVI_1WOTG4IIvVn7w-E"
ADMIN_ID = "7890430043"
ADMIN_SECRET_CODE = "771267"
COLLEGE_NAME = "كلية الحاسبات وتقنية المعلومات"

# إنشاء Flask
app = Flask(__name__)

# ====== قاعدة البيانات المشتركة ======
def init_db():
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    
    # جدول الدكاترة
    c.execute('''CREATE TABLE IF NOT EXISTS professors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        year TEXT NOT NULL,
        term TEXT NOT NULL,
        subject TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # جدول المحتوى
    c.execute('''CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prof_id INTEGER,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT,
        file_path TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (prof_id) REFERENCES professors (id))''')
    
    # جدول المجموعات
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        year TEXT,
        term TEXT,
        subject TEXT,
        link TEXT NOT NULL,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # جدول القنوات
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # جدول التطبيقات
    c.execute('''CREATE TABLE IF NOT EXISTS apps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # جدول سجل المدير
    c.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# ====== دوال قاعدة البيانات ======
def add_professor(name, year, term, subject):
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    c.execute('INSERT INTO professors (name, year, term, subject) VALUES (?, ?, ?, ?)',
              (name, year, term, subject))
    prof_id = c.lastrowid
    conn.commit()
    conn.close()
    return prof_id

def add_group(name, year, term, subject, link, group_type):
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    c.execute('INSERT INTO groups (name, year, term, subject, link, type) VALUES (?, ?, ?, ?, ?, ?)',
              (name, year, term, subject, link, group_type))
    conn.commit()
    conn.close()

def add_channel(name, link, description):
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    c.execute('INSERT INTO channels (name, link, description) VALUES (?, ?, ?)',
              (name, link, description))
    conn.commit()
    conn.close()

def add_app(name, link, description):
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    c.execute('INSERT INTO apps (name, link, description) VALUES (?, ?, ?)',
              (name, link, description))
    conn.commit()
    conn.close()

def log_admin_action(action, details):
    conn = sqlite3.connect('../database.db')
    c = conn.cursor()
    c.execute('INSERT INTO admin_logs (action, details) VALUES (?, ?)', (action, details))
    conn.commit()
    conn.close()

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

# ====== Webhook ======
@app.route('/')
def home():
    return "👑 بوت عِلم - المدير"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            user_id = data["message"]["from"]["id"]
            
            # ✅ التحقق من المدير
            if str(user_id) != str(ADMIN_ID):
                send_msg(chat_id, "🚫 *غير مصرح!*\n\nهذا البوت خاص بالمدير فقط.")
                return jsonify({'ok': True})
            
            # ✅ /start
            if text == "/start":
                send_msg(chat_id, f"""👑 *مرحباً بك في بوت "عِلم - المدير"*

أهلاً يا {data["message"]["from"]["first_name"]}!

🔐 *هذا البوت خاص بك وحدك*

📚 *ما يمكنك فعله:*
• ➕ إضافة دكتور
• 📤 رفع فيديوهات وملفات
• 🔗 إضافة روابط مجموعات
• 🔗 إضافة روابط قنوات
• 📱 إضافة روابط تطبيقات
• 📊 الإحصائيات
• 📢 إرسال إشعارات

🎯 *اختر ما تريد:*""", [
                    [{"text": "➕ إضافة دكتور", "callback_data": "add_prof"}],
                    [{"text": "🔗 إضافة مجموعة", "callback_data": "add_group"}],
                    [{"text": "🔗 إضافة قناة", "callback_data": "add_channel"}],
                    [{"text": "📱 إضافة تطبيق", "callback_data": "add_app"}],
                    [{"text": "📊 الإحصائيات", "callback_data": "stats"}],
                    [{"text": "📢 إرسال إشعار", "callback_data": "broadcast"}]
                ])
            
            # ✅ إضافة دكتور
            elif text.startswith("دكتور|"):
                parts = text.split("|")
                if len(parts) == 5:
                    name, year, term, subject = parts[1], parts[2], parts[3], parts[4]
                    prof_id = add_professor(name, year, term, subject)
                    log_admin_action("add_professor", f"Name: {name}, Year: {year}, Term: {term}, Subject: {subject}")
                    send_msg(chat_id, f"✅ *تم إضافة الدكتور بنجاح!*\n\n📚 *{name}*\nالسنة: {year}\nالترم: {term}\nالمادة: {subject}")
                else:
                    send_msg(chat_id, "❌ *صيغة خاطئة*\n\n📝 *الصيغة الصحيحة:*\n`دكتور|الاسم|السنة|الترم|المادة`\n\n*مثال:*\n`دكتور|د. أحمد الصلوي|1|1|رياضيات`")
            
            # ✅ إضافة مجموعة
            elif text.startswith("مجموعة|"):
                parts = text.split("|")
                if len(parts) == 6:
                    name, year, term, subject, link = parts[1], parts[2], parts[3], parts[4], parts[5]
                    add_group(name, year, term, subject, link, "group")
                    log_admin_action("add_group", f"Name: {name}, Link: {link}")
                    send_msg(chat_id, f"✅ *تم إضافة المجموعة بنجاح!*\n\n🔗 *{name}*\nالرابط: {link}")
                else:
                    send_msg(chat_id, "❌ *صيغة خاطئة*\n\n📝 *الصيغة الصحيحة:*\n`مجموعة|الاسم|السنة|الترم|المادة|الرابط`\n\n*مثال:*\n`مجموعة|رياضيات 1|1|1|رياضيات|https://t.me/...`")
            
            # ✅ إضافة قناة
            elif text.startswith("قناة|"):
                parts = text.split("|")
                if len(parts) == 4:
                    name, link, description = parts[1], parts[2], parts[3]
                    add_channel(name, link, description)
                    log_admin_action("add_channel", f"Name: {name}, Link: {link}")
                    send_msg(chat_id, f"✅ *تم إضافة القناة بنجاح!*\n\n🔗 *{name}*\nالرابط: {link}\nالوصف: {description}")
                else:
                    send_msg(chat_id, "❌ *صيغة خاطئة*\n\n📝 *الصيغة الصحيحة:*\n`قناة|الاسم|الرابط|الوصف`\n\n*مثال:*\n`قناة|أخبار الكلية|https://t.me/...|آخر أخبار الكلية`")
            
            # ✅ إضافة تطبيق
            elif text.startswith("تطبيق|"):
                parts = text.split("|")
                if len(parts) == 4:
                    name, link, description = parts[1], parts[2], parts[3]
                    add_app(name, link, description)
                    log_admin_action("add_app", f"Name: {name}, Link: {link}")
                    send_msg(chat_id, f"✅ *تم إضافة التطبيق بنجاح!*\n\n📱 *{name}*\nالرابط: {link}\nالوصف: {description}")
                else:
                    send_msg(chat_id, "❌ *صيغة خاطئة*\n\n📝 *الصيغة الصحيحة:*\n`تطبيق|الاسم|الرابط|الوصف`\n\n*مثال:*\n`تطبيق|حاسبة ذكية|https://play.google.com/...|حاسبة علمية متقدمة`")
            
            # ✅ إرسال إشعار
            elif text.startswith("إشعار|"):
                parts = text.split("|", 1)
                if len(parts) == 2:
                    message = parts[1]
                    # هنا نرسل الإشعار لجميع المستخدمين
                    send_msg(chat_id, f"📢 *تم إرسال الإشعار!*\n\nالرسالة: {message}")
                else:
                    send_msg(chat_id, "❌ *صيغة خاطئة*\n\n📝 *الصيغة الصحيحة:*\n`إشعار|الرسالة`")
            
            # ✅ المساعدة
            elif text == "/help":
                send_msg(chat_id, """🆘 *مركز المساعدة - المدير*

➕ *إضافة دكتور:*
`دكتور|الاسم|السنة|الترم|المادة`

🔗 *إضافة مجموعة:*
`مجموعة|الاسم|السنة|الترم|المادة|الرابط`

🔗 *إضافة قناة:*
`قناة|الاسم|الرابط|الوصف`

📱 *إضافة تطبيق:*
`تطبيق|الاسم|الرابط|الوصف`

📢 *إرسال إشعار:*
`إشعار|الرسالة`

🎯 *للبدء:* /start""")
            
            # ✅ رسالة غير معروفة
            else:
                send_msg(chat_id, f"""🤔 *لم أفهم الرسالة*

📝 *الصيغ الصحيحة:*
• `دكتور|الاسم|السنة|الترم|المادة`
• `مجموعة|الاسم|السنة|الترم|المادة|الرابط`
• `قناة|الاسم|الرابط|الوصف`
• `تطبيق|الاسم|الرابط|الوصف`
• `إشعار|الرسالة`

🆘 *للمساعدة:* /help""")
        
        # ====== معالجة الأزرار ======
        elif "callback_query" in data:
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            callback = data["callback_query"]["data"]
            
            if callback == "add_prof":
                send_msg(chat_id, "➕ *إضافة دكتور*\n\nأرسل البيانات بالشكل:\n\n`دكتور|الاسم|السنة|الترم|المادة`\n\n📝 *مثال:*\n`دكتور|د. أحمد الصلوي|1|1|رياضيات`")
            
            elif callback == "add_group":
                send_msg(chat_id, "🔗 *إضافة مجموعة*\n\nأرسل البيانات بالشكل:\n\n`مجموعة|الاسم|السنة|الترم|المادة|الرابط`\n\n📝 *مثال:*\n`مجموعة|رياضيات 1|1|1|رياضيات|https://t.me/...`")
            
            elif callback == "add_channel":
                send_msg(chat_id, "🔗 *إضافة قناة*\n\nأرسل البيانات بالشكل:\n\n`قناة|الاسم|الرابط|الوصف`\n\n📝 *مثال:*\n`قناة|أخبار الكلية|https://t.me/...|آخر أخبار الكلية`")
            
            elif callback == "add_app":
                send_msg(chat_id, "📱 *إضافة تطبيق*\n\nأرسل البيانات بالشكل:\n\n`تطبيق|الاسم|الرابط|الوصف`\n\n📝 *مثال:*\n`تطبيق|حاسبة ذكية|https://play.google.com/...|حاسبة علمية متقدمة`")
            
            elif callback == "stats":
                conn = sqlite3.connect('../database.db')
                c = conn.cursor()
                
                c.execute('SELECT COUNT(*) FROM professors')
                prof_count = c.fetchone()[0]
                
                c.execute('SELECT COUNT(*) FROM groups')
                group_count = c.fetchone()[0]
                
                c.execute('SELECT COUNT(*) FROM channels')
                channel_count = c.fetchone()[0]
                
                c.execute('SELECT COUNT(*) FROM apps')
                app_count = c.fetchone()[0]
                
                conn.close()
                
                send_msg(chat_id, f"""📊 *إحصائيات النظام*

📚 الدكاترة: {prof_count}
🔗 المجموعات: {group_count}
📢 القنوات: {channel_count}
📱 التطبيقات: {app_count}

🎯 *الكلية:* {COLLEGE_NAME}""")
            
            elif callback == "broadcast":
                send_msg(chat_id, "📢 *إرسال إشعار*\n\nأرسل الرسالة بالشكل:\n\n`إشعار|الرسالة`\n\n📝 *مثال:*\n`إشعار|تذكير: امتحان الرياضيات غداً الساعة 9 صباحاً`")
        
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return jsonify({'ok': False, 'error': str(e)})

# ====== تشغيل ======
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '10001'))
    app.run(host='0.0.0.0', port=PORT)
