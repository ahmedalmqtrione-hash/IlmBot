"""
👑 لوحة تحكم المدير
-------------------
هنا يتحكم المالك بالنظام كله!
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import ADMIN_SECRET_CODE, ADMIN_ID, COLLEGE_NAME
from bot.database import (
    add_professor, add_content, get_all_years,
    get_professors_by_year_term, get_professor_content,
    log_activity
)

logger = logging.getLogger(__name__)

# حالات المحادثة
WAITING_CODE, ADMIN_MENU, ADD_PROF_NAME, ADD_PROF_YEAR, ADD_PROF_TERM, ADD_PROF_SUBJECT = range(6)

# ====== تسجيل الدخول ======
async def admin_login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بداية تسجيل الدخول"""
    user = update.effective_user
    
    if str(user.id) != str(ADMIN_ID):
        log_activity(user.id, "unauthorized_admin_attempt", f"User: {user.full_name}")
        await update.message.reply_text(
            "🚫 *غير مصرح!*\n\n"
            "هذه المنطقة محمية.\n"
            "تم تسجيل محاولتك.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👑 *لوحة تحكم المدير*\n\n"
        "🔐 أرسل *رمز الدخول* الآن:",
        parse_mode='Markdown'
    )
    return WAITING_CODE

# ====== التحقق من الرمز ======
async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق وعرض القائمة"""
    user = update.effective_user
    text = update.message.text
    
    if text != ADMIN_SECRET_CODE:
        log_activity(user.id, "wrong_admin_code", f"Entered: {text}")
        await update.message.reply_text(
            "❌ *رمز خاطئ!*\n\n"
            "🚨 تم إرسال تنبيه أمان.\n"
            "المحاولة مسجلة.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    log_activity(user.id, "admin_login_success", "Access granted")
    
    keyboard = [
        [InlineKeyboardButton("➕ إضافة دكتور", callback_data="admin_add_prof")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 إرسال إشعار", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📋 قائمة الدكاترة", callback_data="admin_list_profs")],
        [InlineKeyboardButton("🗑️ حذف محتوى", callback_data="admin_delete")],
        [InlineKeyboardButton("🔒 تسجيل الخروج", callback_data="admin_logout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "✅ *تم تسجيل الدخول!*\n\n"
        "👑 مرحباً يا صاحب النظام!\n\n"
        f"🏛️ *{COLLEGE_NAME}*\n\n"
        "اختر ما تريد فعله:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return ADMIN_MENU
