"""
🎮 معالجات الأوامر
------------------
هنا يعيش "الدماغ" الذي يفهم الطالب!
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from sympy import sympify, solve, simplify, latex
from sympy.parsing.sympy_parser import parse_expr

from bot.config import WELCOME_MESSAGE, ADMIN_WELCOME, COLLEGE_NAME, DEVELOPER_NAME, CONTACT_NUMBERS
from bot.database import (
    get_all_years, get_terms_by_year, get_professors_by_year_term,
    get_professor_by_name, get_professor_content, log_activity
)

logger = logging.getLogger(__name__)

# ====== /start ======
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أول ما يدخل الطالب"""
    user = update.effective_user
    
    log_activity(user.id, "start", f"User: {user.full_name}")
    
    # تسجيل الطالب
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO students (id, username, full_name) VALUES (?, ?, ?)',
        (user.id, user.username, user.full_name)
    )
    conn.commit()
    conn.close()
    
    # أزرار السنوات
    years = get_all_years()
    if not years:
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

# ====== /help ======
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المساعدة"""
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

# ====== الآلة الحاسبة ======
async def calculator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حل المعادلات"""
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
    user = update.effective_user
    log_activity(user.id, "calculator", expr)
    
    try:
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

# ====== OCR ======
async def ocr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الصور"""
    user = update.effective_user
    log_activity(user.id, "ocr", "Photo received")
    
    await update.message.reply_text(
        "📸 *جاري تحليل الصورة...*\n\n"
        "⏳ أقوم بـ:\n"
        "1. قراءة النص من الصورة (OCR)\n"
        "2. تحليل المعادلة الرياضية\n"
        "3. حلها خطوة بخطوة\n\n"
        "⚠️ *ملاحظة:* تأكد أن الصورة واضحة وتحتوي على معادلة واحدة",
        parse_mode='Markdown'
    )
    
    await update.message.reply_text(
        "🎯 *تم استلام الصورة!*\n\n"
        "للأسف، OCR يحتاج تثبيت إضافي في Termux:\n"
        "```\n"
        "pkg install tesseract\n"
        "pkg install tesseract-data-eng\n"
        "pkg install tesseract-data-ara\n"
        "```\n\n"
        "بعد التثبيت، سأستطيع قراءة أي معادلة من الصورة! 🚀",
        parse_mode='Markdown'
    )

# ====== البحث الذكي ======
async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """البحث عن الدكاترة"""
    user = update.effective_user
    text = update.message.text
    
    log_activity(user.id, "search", text)
    
    professors = get_professor_by_name(text)
    
    if professors:
        response = f"👨‍🏫 *نتائج البحث عن:* `{text}`\n\n"
        
        for prof in professors:
            prof_id, name, year, term, subject, created = prof
            
            response += (
                f"📚 *{name}*\n"
                f"السنة: {year} | الترم: {term}\n"
                f"المادة: {subject}\n"
                f"─────────────────\n"
            )
            
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
            
            response += "\n"
        
        keyboard = [
            [InlineKeyboardButton("📖 المحاضرات", callback_data=f"lectures:{prof_id}")],
            [InlineKeyboardButton("🎥 الفيديوهات", callback_data=f"videos:{prof_id}")],
            [InlineKeyboardButton("📄 الملفات", callback_data=f"files:{prof_id}")],
            [InlineKeyboardButton("📝 الامتحانات", callback_data=f"exams:{prof_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        
    else:
        ai_response = await ai_process_message(text, user.id)
        await update.message.reply_text(ai_response, parse_mode='Markdown')

# ====== الذكاء الاصطناعي ======
async def ai_process_message(text, user_id):
    """معالجة الرسائل بالذكاء الاصطناعي"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['مرحبا', 'اهلا', 'سلام', 'هاي', 'هلا']):
        return (
            "🌟 *أهلاً وسهلاً!*\n\n"
            "أنا عِلم، مساعدك الأكاديمي الذكي! 🤖\n\n"
            "كيف يمكنني مساعدتك اليوم؟\n\n"
            "جرب:\n"
            "• كتابة اسم دكتور للبحث\n"
            "• /calc لحل المعادلات\n"
            "• /start للتنقل بين السنوات"
        )
    
    elif any(word in text_lower for word in ['امتحان', 'اختبار', 'مذاكرة', 'قلق', 'خايف']):
        return (
            "💪 *لا تقلق!*\n\n"
            "أنا هنا لأساعدك في المذاكرة! 📚\n\n"
            "جرب:\n"
            "• كتابة اسم الدكتور للحصول على المحتوى\n"
            "• `/calc` لحل المعادلات\n"
            "• إرسال صورة لمعادلة صعبة\n\n"
            "أي مادة تريد المذاكرة لها؟"
        )
    
    elif any(word in text_lower for word in ['شكرا', 'تسلم', 'يعطيك العافية', 'مشكور']):
        return (
            "🌟 *العفو!*\n\n"
            "أنا هنا دائماً لخدمتك! 💙\n\n"
            "هل تحتاج شيئاً آخر؟\n"
            "جرب البحث عن دكتور أو حل معادلة!"
        )
    
    elif any(word in text_lower for word in ['دكتور', 'استاذ', 'محاضر', 'دكتورة']):
        return (
            "👨‍🏫 *البحث عن دكتور*\n\n"
            "يمكنك البحث بإحدى الطرق:\n\n"
            "1️⃣ *التنقل:*\n"
            "   اضغط /start → اختر السنة → الترم → الدكتور\n\n"
            "2️⃣ *البحث المباشر:*\n"
            "   اكتب اسم الدكتور مباشرة\n\n"
            "3️⃣ *قائمة الدكاترة:*\n"
            "   اكتب: أريد قائمة الدكاترة"
        )
    
    else:
        return (
            f"🤔 *فهمتك!*\n\n"
            f"أنت قلت: `{text}`\n\n"
            f"يمكنني مساعدتك في:\n"
            f"• 🔢 حل المعادلات: `/calc 2*x+3=7`\n"
            f"• 👨‍🏫 البحث عن دكتور: اكتب اسمه\n"
            f"• 📸 حل من صورة: أرسل صورة مباشرة\n"
            f"• 📚 التنقل: /start\n\n"
            f"ما الذي تريده بالضبط؟ 💡"
        )

# ====== معالجة الأزرار ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة ضغط الأزرار"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("year:"):
        year = data.split(":")[1]
        terms = get_terms_by_year(year)
        
        if not terms:
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
        
        professors = get_professors_by_year_term(year, term)
        
        if professors:
            keyboard = []
            for prof in professors:
                keyboard.append([InlineKeyboardButton(prof[1], callback_data=f"prof:{prof[0]}")])
            
            keyboard.append([InlineKeyboardButton("🔍 بحث بالاسم", callback_data="search_name")])
            
            await query.edit_message_text(
                f"👨‍🏫 *دكاترة {year} - {term}*\n\nاختر دكتوراً:",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                f"⚠️ *لا يوجد دكاترة مسجلين في {year} - {term}*\n\n"
                f"يمكنك إضافة دكاترة من لوحة التحكم (/admin)",
                parse_mode='Markdown'
            )
    
    elif data.startswith("prof:"):
        prof_id = int(data.split(":")[1])
        content = get_professor_content(prof_id)
        
        lectures = [c for c in content if c[3] == 'lecture']
        videos = [c for c in content if c[3] == 'video']
        files = [c for c in content if c[3] == 'file']
        exams = [c for c in content if c[3] == 'exam']
        
        response = "📚 *محتوى الدكتور*\n\n"
        
        if lectures:
            response += "📖 *المحاضرات:*\n"
            for lec in lectures:
                response += f"• {lec[4]}\n"
            response += "\n"
        
        if videos:
            response += "🎥 *الفيديوهات:*\n"
            for vid in videos:
                response += f"• [{vid[4]}]({vid[5]})\n" if vid[5] else f"• {vid[4]}\n"
            response += "\n"
        
        if files:
            response += "📄 *الملفات:*\n"
            for f in files:
                response += f"• {f[4]}\n"
            response += "\n"
        
        if exams:
            response += "📝 *الامتحانات:*\n"
            for ex in exams:
                response += f"• {ex[4]}\n"
            response += "\n"
        
        if not any([lectures, videos, files, exams]):
            response += "⚠️ لا يوجد محتوى مسجل بعد.\n"
            response += "يمكنك إضافة محتوى من لوحة التحكم (/admin)"
        
        await query.edit_message_text(response, parse_mode='Markdown')
