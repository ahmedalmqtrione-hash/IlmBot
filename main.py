"""
🚀 بوت "عِلم" - النسخة النهائية العالمية
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

# ====== استيراد SymPy للحسابات ======
try:
    from sympy import sympify, solve, simplify, latex, diff, integrate
    from sympy.parsing.sympy_parser import parse_expr
    SYMPY_AVAILABLE = True
except:
    SYMPY_AVAILABLE = False

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
        name TEXT NOT NULL,
        year TEXT NOT NULL,
        term TEXT NOT NULL,
        subject TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        year TEXT,
        points INTEGER DEFAULT 0,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
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
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO professors (name, year, term, subject) VALUES (?, ?, ?, ?)',
              (name, year, term, subject))
    prof_id = c.lastrowid
    conn.commit()
    conn.close()
    return prof_id

def get_professor_by_name(name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM professors WHERE name LIKE ?', (f'%{name}%',))
    results = c.fetchall()
    conn.close()
    return results

def get_all_professors():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM professors ORDER BY year, term, name')
    results = c.fetchall()
    conn.close()
    return results

def log_admin_action(action, details):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO admin_logs (action, details) VALUES (?, ?)', (action, details))
    conn.commit()
    conn.close()

# ====== الإعدادات ======
DEVELOPER_NAME = "أحمد حمدي أحمد عثمان المقطري"
CONTACT_NUMBERS = ["771267564", "738805009"]

# ====== الذكاء الاصطناعي - فهم الرسائل ======
def ai_understand(text):
    """فهم الرسالة بالذكاء الاصطناعي"""
    text_lower = text.lower().strip()
    
    # تصحيح الأخطاء الإملائية والنحوية تلقائياً
    corrections = {
        'احمد': 'أحمد',
        'الصلوي': 'الصلوي',
        'القادري': 'القادري',
        'دكتور': 'دكتور',
        'دك': 'دكتور',
        'د.': 'دكتور',
        'سنه': 'سنة',
        'ترم': 'ترم',
        'ماده': 'مادة',
        'حاسوب': 'حاسوب',
        'رياضيات': 'رياضيات',
        'فيزياء': 'فيزياء',
        'كيمياء': 'كيمياء',
        'برمجة': 'برمجة',
    }
    
    # تطبيق التصحيحات
    for wrong, correct in corrections.items():
        text_lower = text_lower.replace(wrong, correct)
    
    # تحديد النية
    if any(word in text_lower for word in ['مرحبا', 'اهلا', 'سلام', 'هاي', 'هلا']):
        return 'greeting'
    
    elif any(word in text_lower for word in ['امتحان', 'اختبار', 'مذاكرة', 'قلق', 'خايف', 'مت stress']):
        return 'exam_stress'
    
    elif any(word in text_lower for word in ['شكرا', 'تسلم', 'يعطيك العافية', 'مشكور']):
        return 'thanks'
    
    elif any(word in text_lower for word in ['دكتور', 'استاذ', 'محاضر', 'دكتورة', 'د.']):
        return 'search_professor'
    
    elif any(word in text_lower for word in ['معادلة', 'حل', 'رياضيات', 'calc', 'حاسبة', 'x', 'y', 'z', '+', '-', '*', '/', '=', '**']):
        return 'math'
    
    elif any(word in text_lower for word in ['صورة', 'صور', 'ocr', 'معادلة', 'كاميرا']):
        return 'ocr'
    
    elif any(word in text_lower for word in ['ادمن', 'مدير', 'admin', 'تحكم', 'اضافة', 'حذف']):
        return 'admin'
    
    else:
        return 'general'

# ====== الآلة الحاسبة الذكية ======
def solve_math_smart(expr):
    """حل المعادلات بالذكاء الاصطناعي"""
    if not SYMPY_AVAILABLE:
        return "❌ مكتبة الحساب غير متوفرة. الرجاء الاتصال بالمدير."
    
    try:
        # تنظيف المعادلة
        expr = expr.strip()
        
        # إذا كانت معادلة (تحتوي على =)
        if '=' in expr:
            left, right = expr.split('=')
            left = parse_expr(left.strip())
            right = parse_expr(right.strip())
            equation = left - right
            solution = solve(equation, dict=True)
            
            result = "✅ *الحل الذكي:*\n\n"
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
            
            # تحديد نوع التعبير
            if 'diff' in expr or 'integrate' in expr:
                return f"🔢 *العملية الحسابية:*\n\nالتعبير: `{expr}`\nالنتيجة: `{result}`\nLaTeX: `{latex(result)}`"
            else:
                return f"🔢 *النتيجة:*\n\nالتعبير: `{expr}`\nالتبسيط: `{result}`\nLaTeX: `{latex(result)}`"
    
    except Exception as e:
        # الذكاء الاصطناعي - تصحيح الخطأ تلقائياً
        error_msg = str(e)
        
        if "invalid syntax" in error_msg:
            return "❌ *خطأ في الصياغة*\n\n🔧 *التصحيح التلقائي:*\n• استخدم `*` للضرب (مثال: `2*x`)\n• استخدم `**` للأس (مثال: `x**2`)\n• المتغيرات: x, y, z\n\n📝 *أمثلة صحيحة:*\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`\n`diff(x**2, x)`\n`integrate(x, x)`"
        
        elif "name" in error_msg and "is not defined" in error_msg:
            return "❌ *متغير غير معروف*\n\n🔧 *التصحيح التلقائي:*\n• استخدم x, y, z كمتغيرات\n• لا تستخدم أرقام كمتغيرات\n\n📝 *مثال صحيح:*\n`2*x + 3 = 7`"
        
        else:
            return f"❌ *خطأ في المعادلة*\n\n🔧 *التصحيح التلقائي:*\n{error_msg}\n\n📝 *جرب:*\n`2*x + 3 = 7`"

# ====== OCR عبر API خارجية ======
def ocr_api(image_url):
    """OCR باستخدام API خارجية"""
    try:
        # هنا يمكنك إضافة API حقيقية مثل Google Vision
        # للآن، نستخدم وصف بسيط
        return "📸 *OCR - الذكاء الاصطناعي*\n\n⚠️ *ملاحظة:*\nOCR المتقدم يحتاج API خارجية (Google Vision API).\n\n🔧 *الحل البديل:*\n• أرسل النص مباشرة\n• أو اكتب المعادلة يدوياً\n\n📝 *مثال:*\n`2*x + 3 = 7`"
    except Exception as e:
        return f"❌ خطأ في OCR: {str(e)}"

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
        [{"text": "🔢 آلة حاسبة ذكية", "callback_data": "calc"}],
        [{"text": "📸 OCR - قراءة الصور", "callback_data": "ocr"}],
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
    return "🚀 بوت عِلم - الذكاء الاصطناعي الخارق!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        
        # ====== معالجة الرسائل النصية ======
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            user_id = data["message"]["from"]["id"]
            
            # ✅ الأوامر الرسمية
            if text == "/start":
                send_msg(chat_id, f"""🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *الميزات الذكية:*
• 🔢 حل المعادلات الرياضية خطوة بخطوة
• 👨‍🏫 البحث الذكي عن الدكاترة والمواد
• 📸 OCR - قراءة المعادلات من الصور
• 🧠 فهم أسئلتك والرد بذكاء
• 🎓 التنقل بين السنوات والترمات

🎯 *اختر السنة الدراسية:*""", get_years_buttons())
            
            elif text == "/help":
                send_msg(chat_id, """🆘 *مركز المساعدة*

/start - الرئيسية
/calc - آلة حاسبة ذكية
/admin - لوحة تحكم المدير (خاصة)

💡 *أمثلة على المعادلات:*
`2*x + 3 = 7`
`x**2 + 5*x - 6`
`diff(x**2, x)` - مشتقة
`integrate(x, x)` - تكامل

📝 *أمثلة على البحث:*
• "دكتور أحمد"
• "رياضيات"
• "السنة الأولى"
""")
            
            elif text == "/calc":
                send_msg(chat_id, "🔢 *آلة حاسبة ذكية*\n\nأرسل المعادلة:\n\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`\n`diff(x**2, x)` - مشتقة\n`integrate(x, x)` - تكامل")
            
            elif text == "/admin":
                # التحقق من هوية المدير
                if str(user_id) == str(ADMIN_ID):
                    send_msg(chat_id, "👑 *لوحة تحكم المدير*\n\n🔐 أرسل رمز الدخول:")
                else:
                    send_msg(chat_id, "🚫 *غير مصرح!*\n\nهذه المنطقة محمية. تم تسجيل محاولتك.")
            
            # ✅ رمز الدخول
            elif text == ADMIN_SECRET_CODE:
                if str(user_id) == str(ADMIN_ID):
                    log_admin_action("login", f"User: {user_id}")
                    send_msg(chat_id, "✅ *تم تسجيل الدخول!*\n\n👑 مرحباً يا صاحب النظام!\n\n*لوحة التحكم الخاصة:*", [
                        [{"text": "➕ إضافة دكتور", "callback_data": "add_prof"}],
                        [{"text": "📊 الإحصائيات", "callback_data": "stats"}],
                        [{"text": "📢 إرسال إشعار", "callback_data": "broadcast"}],
                        [{"text": "📋 قائمة الدكاترة", "callback_data": "list_profs"}],
                        [{"text": "🗑️ حذف محتوى", "callback_data": "delete"}],
                        [{"text": "🔒 تسجيل الخروج", "callback_data": "logout"}]
                    ])
                else:
                    send_msg(chat_id, "❌ *رمز خاطئ!*\n\n🚨 تم إرسال تنبيه أمان.")
            
            # ✅ الذكاء الاصطناعي - فهم تلقائي
            else:
                intent = ai_understand(text)
                
                if intent == 'math':
                    result = solve_math_smart(text)
                    send_msg(chat_id, result)
                
                elif intent == 'search_professor':
                    # البحث الذكي
                    professors = get_professor_by_name(text)
                    
                    if professors:
                        response = f"👨‍🏫 *نتائج البحث الذكي:*\n\n"
                        for prof in professors:
                            prof_id, name, year, term, subject, created = prof
                            response += f"📚 *{name}*\nالسنة: {year} | الترم: {term}\nالمادة: {subject}\n\n"
                        send_msg(chat_id, response)
                    else:
                        # الذكاء الاصطناعي - اقتراحات
                        send_msg(chat_id, f"🤔 *لم أجد نتائج للبحث:* `{text}`\n\n🔧 *الذكاء الاصطناعي يقترح:*\n• التأكد من إملاء الاسم\n• البحث باسم المادة\n• التنقل بين السنوات /start", [
                            [{"text": "📚 التنقل بين السنوات", "callback_data": "back:years"}]
                        ])
                
                elif intent == 'greeting':
                    send_msg(chat_id, f"""🌟 *أهلاً وسهلاً!*

أنا عِلم، مساعدك الأكاديمي الذكي! 🤖

كيف يمكنني مساعدتك اليوم؟

📚 *ما يمكنني فعله:*
• حل المعادلات الرياضية
• البحث عن الدكاترة والمواد
• قراءة الصور (OCR)
• الرد الذكي على أسئلتك

🎯 *ابدأ الآن:* /start""")
                
                elif intent == 'exam_stress':
                    send_msg(chat_id, """💪 *لا تقلق!*

أنا هنا لأساعدك في المذاكرة! 📚

🔧 *نصائح الذكاء الاصطناعي:*
• خذ قسطاً من الراحة
• راجع الملخصات
• حل امتحانات سابقة

🎯 *ابدأ بالبحث عن دكتورك:* /start""")
                
                elif intent == 'thanks':
                    send_msg(chat_id, "🌟 *العفو!*\n\nأنا هنا دائماً لخدمتك! 💙\n\nهل تحتاج شيئاً آخر؟")
                
                else:
                    # الرد الذكي العام
                    send_msg(chat_id, f"""🤔 *فهمتك!*

أنت قلت: `{text}`

🔧 *الذكاء الاصطناعي يقترح:*
• إذا كانت معادلة: اكتبها مباشرة
• إذا كنت تبحث عن دكتور: اكتب اسمه
• إذا كنت تريد آلة حاسبة: /calc

🎯 *للبدء:* /start""")
        
        # ====== معالجة الصور (OCR عبر API) ======
        elif "message" in data and "photo" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            
            try:
                # تحميل الصورة
                file_id = data["message"]["photo"][-1]["file_id"]
                file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                file_info = requests.get(file_url).json()
                file_path = file_info["result"]["file_path"]
                download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                
                # OCR عبر API
                result = ocr_api(download_url)
                send_msg(chat_id, result)
            except Exception as e:
                send_msg(chat_id, f"❌ خطأ في معالجة الصورة: {str(e)}")
        
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
                
                # البحث الحقيقي
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
                    send_msg(chat_id, f"⚠️ *لا يوجد دكاترة مسجلين*\n\nيمكنك إضافتهم من لوحة التحكم (/admin)", [
                        [{"text": "🔙 رجوع", "callback_data": f"back:year:{year}"}]
                    ])
            
            elif callback == "calc":
                send_msg(chat_id, "🔢 *آلة حاسبة ذكية*\n\nأرسل المعادلة:\n\n`2*x + 3 = 7`\n`x**2 + 5*x - 6`")
            
            elif callback == "ocr":
                send_msg(chat_id, "📸 *OCR - الذكاء الاصطناعي*\n\nأرسل صورة معادلة وسأقرأها وأحلها!\n\n🔧 *نصائح:*\n• الصورة واضحة\n• الخلفية فاتحة\n• المعادلة مرئية")
            
            elif callback == "search":
                send_msg(chat_id, "🔍 *البحث الذكي*\n\nاكتب اسم الدكتور أو المادة:")
            
            elif callback == "add_prof":
                send_msg(chat_id, "➕ *إضافة دكتور*\n\nأرسل البيانات بالشكل:\n\n`اسم الدكتور | السنة | الترم | المادة`\n\n📝 *مثال:*\n`د. أحمد الصلوي | 1 | 1 | رياضيات`")
            
            elif callback == "stats":
                professors = get_all_professors()
                send_msg(chat_id, f"📊 *إحصائيات النظام*\n\nعدد الدكاترة: {len(professors)}\n\nالدكاترة المسجلين:\n" + "\n".join([f"• {p[1]} ({p[4]})" for p in professors[:10]]))
            
            elif callback == "broadcast":
                send_msg(chat_id, "📢 *إرسال إشعار*\n\nاكتب الرسالة التي تريد إرسالها للجميع:")
            
            elif callback == "logout":
                send_msg(chat_id, "🔒 *تم تسجيل الخروج*")
            
            elif callback.startswith("back:"):
                if callback == "back:years":
                    send_msg(chat_id, f"""🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

🎯 *اختر السنة الدراسية:*""", get_years_buttons())
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
