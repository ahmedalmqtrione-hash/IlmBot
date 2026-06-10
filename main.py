"""
🚀 بوت "عِلم" - النسخة المُصلحة لـ Render
-----------------------------------------
كلية الحاسبات وتقنية المعلومات
المطور: أحمد حمدي أحمد عثمان المقطري
"""

import os
import sys
import logging
import sqlite3
from dotenv import load_dotenv

# تحميل المتغيرات
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التحقق من المتغيرات
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
ADMIN_SECRET_CODE = os.getenv('ADMIN_SECRET_CODE')
COLLEGE_NAME = os.getenv('COLLEGE_NAME', 'كلية الحاسبات')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN غير موجود!")
    sys.exit(1)

logger.info("✅ المتغيرات محملة!")

# استيراد المكتبات
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler, ContextTypes
)

# ====== تهيئة قاعدة البيانات ======
def init_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            year TEXT NOT NULL,
            term TEXT NOT NULL,
            subject TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            file_path TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (professor_id) REFERENCES professors (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            year TEXT,
            points INTEGER DEFAULT 0,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ قاعدة البيانات جاهزة!")

init_database()

# ====== الإعدادات ======
DEVELOPER_NAME = "أحمد حمدي أحمد عثمان المقطري"
CONTACT_NUMBERS = ["771267564", "738805009"]

WELCOME_MESSAGE = f"""
🎓 *مرحباً بك في بوت "عِلم"*

أنا ذكاءك الأكاديمي الشخصي! 🤖

📚 *ما يمكنني فعله:*
• 🔢 حل المعادلات الرياضية خطوة بخطوة
• 📸 قراءة المعادلات من الصور (OCR)
• 👨‍🏫 البحث عن الدكاترة والمواد
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

# ====== دوال المعالجة ======
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO students (id, username, full_name) VALUES (?, ?, ?)',
        (user.id, user.username, user.full_name)
    )
    conn.commit()
    conn.close()
    
    years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة"]
    
    keyboard = []
    for year in years:
        keyboard.append([InlineKeyboardButton(f"📚 {year}", callback_data=f"year:{year}")])
    
    keyboard.append([InlineKeyboardButton("🔍 البحث عن دكتور", callback_data="search_prof")])
    keyboard.append([InlineKeyboardButton("🔢 آلة حاسبة", callback_data="calculator")])
    keyboard.append([InlineKeyboardButton("📸 حل من صورة", callback_data="ocr")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
🆘 *مركز المساعدة - بوت "عِلم"*

*البحث عن الدكاترة:*
1. اختر السنة الدراسية
2. اختر الترم
3. اكتب اسم الدكتور أو اختر من القائمة

*الآلة الحاسبة:*
/calc 2*x + 3 = 7
/calc diff(x**2, x)
/calc integrate(x, x)

*OCR (قراءة الصور):*
أرسل صورة معادلة وسأحلها!

*لوحة المدير:*
/admin

💡 *نصيحة:* يمكنك كتابة اسم الدكتور مباشرة!

─────────────────
👨‍💻 *المطور:* {DEVELOPER_NAME}
📞 *للاستفسارات:* {', '.join(CONTACT_NUMBERS)}
🏛️ *{COLLEGE_NAME}*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def calculator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🔢 *آلة حاسبة ذكية*\n\n"
            "الاستخدام:\n"
            "`/calc 2*x + 3 = 7`\n"
            "`/calc x**2 + 3*x - 4`\n"
            "`/calc diff(x**2, x)` ← مشتقة\n"
            "`/calc integrate(x, x)` ← تكامل\n\n"
            "أرسل معادلتك!",
            parse_mode='Markdown'
        )
        return
    
    expr = ' '.join(context.args)
    
    try:
        from sympy import sympify, solve, simplify, latex
        from sympy.parsing.sympy_parser import parse_expr
        
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
            
            steps = f"\n📐 *خطوات الحل:*\n"
            steps += f"المعادلة: `{latex(equation)} = 0`\n"
            steps += f"التبسيط: `{latex(simplify(equation))}`"
            
            await update.message.reply_text(result + steps, parse_mode='Markdown')
            
        else:
            expr_parsed = parse_expr(expr)
            result = simplify(expr_parsed)
            
            response = (
                f"🔢 *النتيجة:*\n\n"
                f"التعبير: `{expr}`\n"
                f"التبسيط: `{result}`\n"
                f"LaTeX: `{latex(result)}`"
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ *خطأ في المعادلة*\n\n"
            f"تأكد من الصياغة:\n"
            f"• الضرب: `*` أو مسافة\n"
            f"• الأس: `**` (مثال: x**2)\n"
            f"• المتغيرات: x, y, z\n\n"
            f"الخطأ: `{str(e)}`",
            parse_mode='Markdown'
        )

async def ocr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 *جاري تحليل الصورة...*\n\n"
        "⏳ أقوم بـ:\n"
        "1. قراءة النص من الصورة (OCR)\n"
        "2. تحليل المعادلة الرياضية\n"
        "3. حلها خطوة بخطوة\n\n"
        "⚠️ *ملاحظة:* تأكد أن الصورة واضحة",
        parse_mode='Markdown'
    )
    
    await update.message.reply_text(
        "🎯 *تم استلام الصورة!*\n\n"
        "للأسف، OCR يحتاج تثبيت إضافي:\n"
        "```\n"
        "pkg install tesseract\n"
        "pkg install tesseract-data-eng\n"
        "pkg install tesseract-data-ara\n"
        "```\n\n"
        "بعد التثبيت، سأستطيع قراءة أي معادلة! 🚀",
        parse_mode='Markdown'
    )

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if str(user.id) != str(ADMIN_ID):
        await update.message.reply_text(
            "🚫 *غير مصرح!*\n\nهذه المنطقة محمية.",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(
        "👑 *لوحة تحكم المدير*\n\n"
        "🔐 أرسل *رمز الدخول* الآن:",
        parse_mode='Markdown'
    )

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['مرحبا', 'اهلا', 'سلام', 'هاي', 'هلا']):
        await update.message.reply_text(
            "🌟 *أهلاً وسهلاً!*\n\n"
            "أنا عِلم، مساعدك الأكاديمي الذكي! 🤖\n\n"
            "كيف يمكنني مساعدتك اليوم؟\n\n"
            "جرب:\n"
            "• كتابة اسم دكتور للبحث\n"
            "• /calc لحل المعادلات\n"
            "• /start للتنقل بين السنوات",
            parse_mode='Markdown'
        )
    
    elif any(word in text_lower for word in ['امتحان', 'اختبار', 'مذاكرة', 'قلق', 'خايف']):
        await update.message.reply_text(
            "💪 *لا تقلق!*\n\n"
            "أنا هنا لأساعدك في المذاكرة! 📚\n\n"
            "جرب:\n"
            "• كتابة اسم الدكتور للحصول على المحتوى\n"
            "• `/calc` لحل المعادلات\n"
            "• إرسال صورة لمعادلة صعبة\n\n"
            "أي مادة تريد المذاكرة لها؟",
            parse_mode='Markdown'
        )
    
    elif any(word in text_lower for word in ['شكرا', 'تسلم', 'يعطيك العافية', 'مشكور']):
        await update.message.reply_text(
            "🌟 *العفو!*\n\n"
            "أنا هنا دائماً لخدمتك! 💙\n\n"
            "هل تحتاج شيئاً آخر؟",
            parse_mode='Markdown'
        )
    
    elif any(word in text_lower for word in ['دكتور', 'استاذ', 'محاضر', 'دكتورة']):
        await update.message.reply_text(
            "👨‍🏫 *البحث عن دكتور*\n\n"
            "يمكنك البحث بإحدى الطرق:\n\n"
            "1️⃣ *التنقل:*\n"
            "   اضغط /start → اختر السنة → الترم → الدكتور\n\n"
            "2️⃣ *البحث المباشر:*\n"
            "   اكتب اسم الدكتور مباشرة\n\n"
            "3️⃣ *قائمة الدكاترة:*\n"
            "   اكتب: أريد قائمة الدكاترة",
            parse_mode='Markdown'
        )
    
    else:
        await update.message.reply_text(
            f"🤔 *فهمتك!*\n\n"
            f"أنت قلت: `{text}`\n\n"
            f"يمكنني مساعدتك في:\n"
            f"• 🔢 حل المعادلات: `/calc 2*x+3=7`\n"
            f"• 👨‍🏫 البحث عن دكتور: اكتب اسمه\n"
            f"• 📸 حل من صورة: أرسل صورة مباشرة\n"
            f"• 📚 التنقل: /start\n\n"
            f"ما الذي تريده بالضبط؟ 💡",
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("year:"):
        year = data.split(":")[1]
        terms = ["الترم الأول", "الترم الثاني"]
        
        keyboard = []
        for term in terms:
            keyboard.append([InlineKeyboardButton(term, callback_data=f"term:{year}:{term}")])
        
        await query.edit_message_text(
            f"📚 *{year}*\n\nاختر الترم:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("term:"):
        parts = data.split(":")
        year = parts[1]
        term = parts[2]
        
        await query.edit_message_text(
            f"👨‍🏫 *دكاترة {year} - {term}*\n\n"
            f"⚠️ لا يوجد دكاترة مسجلين بعد.\n\n"
            f"يمكنك إضافة دكاترة من لوحة التحكم (/admin)",
            parse_mode='Markdown'
        )

# ====== إنشاء التطبيق ======
application = Application.builder().token(BOT_TOKEN).build()

# ====== تسجيل المعالجات ======
application.add_handler(CommandHandler("start", start_handler))
application.add_handler(CommandHandler("help", help_handler))
application.add_handler(CommandHandler("calc", calculator_handler))
application.add_handler(CommandHandler("admin", admin_handler))
application.add_handler(MessageHandler(filters.PHOTO, ocr_handler))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))

# ====== تشغيل البوت ======
if __name__ == '__main__':
    logger.info("🚀 تشغيل بوت 'عِلم'...")
    logger.info(f"🏛️ {COLLEGE_NAME}")
    logger.info("👨‍💻 المطور: أحمد حمدي أحمد عثمان المقطري")
    
    # التحقق من البيئة
    PORT = int(os.environ.get('PORT', '10000'))
    WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', '')
    
    if WEBHOOK_URL:
        # تشغيل على Render (Webhook)
        WEBHOOK_PATH = f"/{BOT_TOKEN}"
        WEBHOOK_FULL_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        
        logger.info(f"🌐 Webhook URL: {WEBHOOK_FULL_URL}")
        
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_FULL_URL,
            secret_token=BOT_TOKEN
        )
    else:
        # تشغيل محلي (Polling)
        logger.info("🏠 تشغيل محلي (Polling)")
        application.run_polling()

