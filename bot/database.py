"""
🗄️ قاعدة بيانات "عِلم"
---------------------
SQLite - سريعة ولا تحتاج سيرفر!
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = 'database.db'

def init_database():
    """إنشاء الجداول"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # جدول الدكاترة
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
    
    # جدول المحتوى
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
    
    # جدول الطلاب
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
    
    # جدول السجل
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

def add_professor(name, year, term, subject):
    """إضافة دكتور"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO professors (name, year, term, subject) VALUES (?, ?, ?, ?)',
        (name, year, term, subject)
    )
    prof_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prof_id

def add_content(professor_id, content_type, title, url=None, file_path=None, description=None):
    """إضافة محتوى"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO content (professor_id, type, title, url, file_path, description) VALUES (?, ?, ?, ?, ?, ?)',
        (professor_id, content_type, title, url, file_path, description)
    )
    conn.commit()
    conn.close()

def get_professor_by_name(name, year=None, term=None):
    """البحث عن دكتور"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if year and term:
        cursor.execute(
            'SELECT * FROM professors WHERE name LIKE ? AND year = ? AND term = ?',
            (f'%{name}%', year, term)
        )
    else:
        cursor.execute(
            'SELECT * FROM professors WHERE name LIKE ?',
            (f'%{name}%',)
        )
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_professor_content(professor_id):
    """جلب محتوى الدكتور"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM content WHERE professor_id = ? ORDER BY type, created_at',
        (professor_id,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_years():
    """جلب السنوات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT year FROM professors ORDER BY year')
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_terms_by_year(year):
    """جلب الترمات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT term FROM professors WHERE year = ?', (year,))
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def get_professors_by_year_term(year, term):
    """جلب الدكاترة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM professors WHERE year = ? AND term = ?',
        (year, term)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def log_activity(user_id, action, details=None):
    """تسجيل نشاط"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
        (user_id, action, details)
    )
    conn.commit()
    conn.close()
