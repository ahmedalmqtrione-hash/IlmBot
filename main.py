"""
🚀 بوت "عِلم" - النسخة الحقيقية العاملة
-----------------------------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import logging
import sqlite3
import re
from flask import Flask, request, jsonify
import requests

# ====== استيراد مكتبات حقيقية ======
try:
    from sympy import sympify, solve, simplify, latex, diff, integrate
    from sympy.parsing.sympy_parser import parse_expr
    SYMPY_AVAILABLE = True
except:
    SYMPY_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

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

# ====== قاعدة البيانات الحقيقية ======
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # جدول الدكاترة
    c.execute('''CREATE TABLE IF NOT EXISTS professors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        year TEXT NOT NULL,
        term TEXT NOT NULL,
        subject TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # جدول المحتوى (محاضرات، فيديوهات، ملفات، امتحانات)
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
    
    # جدول الطلاب
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        year TEXT,
        points INTEGER DEFAULT 0,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# ====== دوال قاعدة البيانات ======
def add_professor(name, year, term, subject):
    """إضافة دكتور حقيقي"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO professors (name, year, term, subject) VALUES (?, ?, ?, ?)',
              (name, year, term, subject))
    prof_id = c.lastrowid
    conn.commit()
    conn.close()
    return prof_id

def add_content(prof_id, content_type, title, url=None, file_path=None, description=None):
    """إضافة محتوى حقيقي"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO content (prof_id, type, title, url, file_path, description) VALUES (?, ?, ?, ?, ?, ?)',
              (prof_id, content_type, title, url, file_path, description))
    conn.commit()
    conn.close()

def get_professor_by_name(name):
    """البحث الحقيقي عن دكتور"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM professors WHERE name LIKE ?', (f'%{name}%',))
    results = c.fetchall()
    conn.close()
    return results

def get_professor_content(prof_id):
    """جلب محتوى الدكتور الحقيقي"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM content WHERE prof_id = ? ORDER BY type', (prof_id,))
    results = c.fetchall()
    conn.close()
    return results

def get_all_professors():
    """جلب كل الدكاترة"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM professors ORDER BY year, term, name')
    results = c.fetchall()
    conn.close()
    return results

# ====== الإعدادات ======
DEVELOPER_NAME = "أحمد حمدي أحمد عثمان المقطري"
CONTACT_NUMBERS = ["771267564", "738805009"]

WELCOME_MESSAGE = f"""🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *ما يمكنني فعله:*
• 🔢 حل المعادلات الرياضية خطوة بخطوة
• 👨‍🏫 البحث عن الدكاترة والمواد
• 📸 قراءة المعادلات من الصور (OCR)
• 🎥 عرض المحاضرات والفيديوهات
• 📄 تحميل الملفات والامتحانات
• 🧠 فهم أسئلتك والرد بذكاء

🎯 *ابدأ رحلتك:*
اضغط /start للتنقل بين السنوات والترمات
أو اكتب اسم الدكتور مباشرة!

─────────────────
👨‍💻 *المطور:* {DEVELOPER_NAME}
📞 *للاستفسارات:* {', '.join(CONTACT_NUMBERS)}
🏛️ *{COLLEGE_NAME}*
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

# ====== الآلة الحاسبة الحقيقية ======
def solve_math(expr):
    """حل المعادلات الرياضية حقيقياً"""
    if not SYMPY_AVAILABLE:
        return "❌ مكتبة SymPy غير مثبتة. أرسل للمدير ليثبتها."
    
    try:
        # إذا كانت معادلة (تحتوي على =)
        if '=' in expr:
            left, right = expr.split('=')
            left = parse_expr(left.strip())
            right = parse_expr(right.strip())
            equation = left - right
            solution = solve(equation, dict=True)
            
            result = "✅ *الحل:*\n\n"
            for sol in solution:
                for var, val in sol.items():
                    result += f"• `{var}` = `{val}`\n"
            
            result += f"\n📐 *خطوات الحل:*\n"
            result += f"المعادلة: `{latex(equation)} = 0`\n"
            result += f"التبسيط: `{latex(simplify(equation))}`"
            return result
        
        # إذا كان تعبير عادي
        else:
            expr_parsed = parse_expr(expr)
            result = simplify(expr_parsed)
            return f"🔢 *النتيجة:*\n\nالتعبير: `{expr}`\nالتبسيط: `{result}`\nLaTeX: `{latex(result)}`"
    
    except Exception as e:
        return f"❌ *خطأ في المعادلة*\n\nتأكد من الصياغة:\n• الضرب: `*` أو مسافة\n• الأس: `**` (مثال: x**2)\n• المتغيرات: x, y, z\n\nالخطأ: `{str(e)}`"

# ====== OCR الحقيقي ======
def ocr_solve(image_path):
    """قراءة المعادلة من الصورة وحلها حقيقياً"""
    if not OCR_AVAILABLE:
        return "❌ مكتبة OCR غير مثبتة. أرسل للمدير ليثبتها."
    
    try:
        # قراءة الصورة
        img = Image.open(image_path)
        # استخراج النص
        text = pytesseract.image_to_string(img, lang='eng+ara')
        # تنظيف النص
        text = text.strip().replace('\n', ' ')
        
        if not text:
            return "⚠️ لم أستطع قراءة أي نص من الصورة. تأكد أن الصورة واضحة."
        
        # محاولة حل المعادلة
        result = solve_math(text)
        return f"📸 *OCR - قراءة من الصورة*\n\nالمعادلة المقروءة: `{text}`\n\n{result}"
    
    except Exception as e:
        return f"❌ خطأ في OCR: {str(e)}"

# ====== الأزرار ======
def get_years_buttons():
    return [
        [{"text": "📚 السنة الأولى", "callback_data": "year:1"}],
        [{"text": "📚 السنة الثانية", "callback_data": "year:2"}],
        [{"text": "📚 السنة الثالثة", "callback_data": "year:3"}],
        [{"text": "📚 السنة الرابعة", "callback_data": "year:4"}],
        [{"text": "🔢 آلة حاسبة", "callback_data": "calc"}],
        [{"text": "📸 حل من صورة", "callback_data": "ocr"}],
        [{"text": "👨‍🏫 البحث عن دكتور", "callback_data": "search"}]
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
    return "🚀 بوت عِلم يعمل!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        # ====== معالجة الرسائل النصية ======
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            user_id = data["message"]["from"]["id"]
            
            # ✅ الأوامر
            if text == "/start":
                send_msg(chat_id, WELCOME_MESSAGE, get_years_buttons())
            
            elif text == "/help":
                send_msg(chat_id, "🆘 *مركز المساعدة*\n\n/start - الرئيسية\n/calc - آلة حاسبة\n/admin - لوحة تحكم المدير\n\n💡 اكتب اسم الدكتور للبحث!")
            
            elif text == "/calc":
                send_msg(chat_id, "🔢 *آلة حاسبة ذكية*\n\nأرسل المعادلة:\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`\n`diff(x**2, x)` - مشتقة\n`integrate(x, x)` - تكامل")
            
            elif text == "/admin":
                if str(user_id) == str(ADMIN_ID):
                    send_msg(chat_id, "👑 *لوحة تحكم المدير*\n\n🔐 أرسل رمز الدخول:")
                else:
                    send_msg(chat_id, "🚫 *غير مصرح!*")
            
            # ✅ رمز الدخول
            elif text == ADMIN_SECRET_CODE:
                if str(user_id) == str(ADMIN_ID):
                    send_msg(chat_id, "✅ *تم تسجيل الدخول!*\n\n👑 مرحباً يا صاحب النظام!", [
                        [{"text": "➕ إضافة دكتور", "callback_data": "add_prof"}],
                        [{"text": "📊 الإحصائيات", "callback_data": "stats"}],
                        [{"text": "📢 إرسال إشعار", "callback_data": "broadcast"}],
                        [{"text": "📋 قائمة الدكاترة", "callback_data": "list_profs"}],
                        [{"text": "🔒 تسجيل الخروج", "callback_data": "logout"}]
                    ])
                else:
                    send_msg(chat_id, "❌ *رمز خاطئ!*")
            
            # ✅ آلة حاسبة (تبدي بـ = أو رقم أو متغير)
            elif text.startswith('=') or any(c in text for c in '0123456789xyz+-*/^'):
                result = solve_math(text)
                send_msg(chat_id, result)
            
            # ✅ البحث العادي
            else:
                # البحث الحقيقي في قاعدة البيانات
                professors = get_professor_by_name(text)
                
                if professors:
                    response = f"👨‍🏫 *نتائج البحث عن:* `{text}`\n\n"
                    for prof in professors:
                        prof_id, name, year, term, subject, created = prof
                        response += f"📚 *{name}*\nالسنة: {year} | الترم: {term}\nالمادة: {subject}\n\n"
                    
                    # جلب المحتوى
                    content = get_professor_content(prof_id)
                    lectures = [c for c in content if c[3] == 'lecture']
                    videos = [c for c in content if c[3] == 'video']
                    files = [c for c in content if c[3] == 'file']
                    exams = [c for c in content if c[3] == 'exam']
                    
                    if lectures:
                        response += f"📖 محاضرات: {len(lectures)}\n"
                    if videos:
                        response += f"🎥 فيديوهات: {len(videos)}\n"
                    if files:
                        response += f"📄 ملفات: {len(files)}\n"
                    if exams:
                        response += f"📝 امتحانات: {len(exams)}\n"
                    
                    send_msg(chat_id, response)
                else:
                    send_msg(chat_id, f"🤔 *لم أجد نتائج للبحث:* `{text}`\n\nجرب:\n• كتابة اسم دكتور آخر\n• /start للتنقل بين السنوات")
        
        # ====== معالجة الصور (OCR) ======
        elif "message" in data and "photo" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            
            if not OCR_AVAILABLE:
                send_msg(chat_id, "❌ *OCR غير متاح*\n\nمكتبة OCR غير مثبتة. أرسل للمدير ليثبتها.")
            else:
                # تحميل الصورة
                file_id = data["message"]["photo"][-1]["file_id"]
                file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                file_info = requests.get(file_url).json()
                file_path = file_info["result"]["file_path"]
                download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                
                # تحميل الصورة
                img_data = requests.get(download_url).content
                with open('temp_image.jpg', 'wb') as f:
                    f.write(img_data)
                
                # OCR
                result = ocr_solve('temp_image.jpg')
                send_msg(chat_id, result)
        
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
                
                # البحث الحقيقي عن دكاترة في هذا الترم
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute('SELECT * FROM professors WHERE year = ? AND term = ?', (year, term))
                professors = c.fetchall()
                conn.close()
                
                if professors:
                    response = f"👨‍🏫 *دكاترة السنة {year} - الترم {term_names.get(term, term)}*\n\n"
                    for prof in professors:
                        prof_id, name, y, t, subject, created = prof
                        response += f"• *{name}* - {subject}\n"
                    send_msg(chat_id, response, [
                        [{"text": "🔙 رجوع", "callback_data": f"back:year:{year}"}]
                    ])
                else:
                    send_msg(chat_id, f"⚠️ *لا يوجد دكاترة مسجلين في السنة {year} - الترم {term_names.get(term, term)}*\n\nيمكنك إضافتهم من لوحة التحكم (/admin)", [
                        [{"text": "🔙 رجوع", "callback_data": f"back:year:{year}"}]
                    ])
            
            elif callback == "calc":
                send_msg(chat_id, "🔢 *آلة حاسبة*\n\nأرسل المعادلة:\n\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`")
            
            elif callback == "ocr":
                send_msg(chat_id, "📸 *OCR - قراءة الصور*\n\nأرسل صورة معادلة وسأقرأها وأحلها!")
            
            elif callback == "search":
                send_msg(chat_id, "🔍 *البحث عن دكتور*\n\nاكتب اسم الدكتور أو المادة:")
            
            elif callback == "add_prof":
                send_msg(chat_id, "➕ *إضافة دكتور*\n\nأرسل البيانات بالشكل:\n\n`اسم الدكتور | السنة | الترم | المادة`\n\nمثال:\n`د. أحمد الصلوي | 1 | 1 | رياضيات`")
            
            elif callback == "stats":
                professors = get_all_professors()
                send_msg(chat_id, f"📊 *إحصائيات النظام*\n\nعدد الدكاترة: {len(professors)}\n\nالدكاترة المسجلين:\n" + "\n".join([f"• {p[1]} ({p[4]})" for p in professors[:10]]))
            
            elif callback == "broadcast":
                send_msg(chat_id, "📢 *إرسال إشعار*\n\nاكتب الرسالة التي تريد إرسالها للجميع:")
            
            elif callback == "logout":
                send_msg(chat_id, "🔒 *تم تسجيل الخروج*")
            
            elif callback.startswith("back:"):
                if callback == "back:years":
                    send_msg(chat_id, WELCOME_MESSAGE, get_years_buttons())
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
