#!/usr/bin/env python3
"""
سكريبت لتوليد ملف .env بقيم آمنة تلقائياً
"""

import secrets
import string
import os

def generate_secure_key(length=32):
    """توليد مفتاح آمن عشوائي (بدون رموز خاصة لتجنب مشاكل Docker)"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_password(length=16):
    """توليد كلمة مرور قوية (بدون رموز خاصة لتجنب مشاكل Docker)"""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def create_env_file():
    """إنشاء ملف .env بقيم آمنة"""
    
    # توليد القيم الآمنة
    secret_key = generate_secure_key(64)  # 64 حرف للأمان الإضافي
    db_encryption_key = generate_secure_key(32)
    mysql_password = generate_password(20)
    
    # محتوى ملف .env
    env_content = f"""# ملف البيئة - تم توليده تلقائياً
# لا تشارك هذا الملف مع أحد!

# مفتاح الأمان الرئيسي للتطبيق
SECRET_KEY={secret_key}

# مفتاح تشفير قاعدة البيانات
DB_ENCRYPTION_KEY={db_encryption_key}

# كلمة مرور قاعدة البيانات MySQL
MYSQL_ROOT_PASSWORD={mysql_password}

# إعدادات الإنتاج
FLASK_ENV=production
"""
    
    # كتابة الملف
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ تم إنشاء ملف .env بنجاح!")
    print("\n🔐 القيم المُولدة:")
    print(f"SECRET_KEY: {secret_key[:20]}...")
    print(f"DB_ENCRYPTION_KEY: {db_encryption_key[:20]}...")
    print(f"MYSQL_ROOT_PASSWORD: {mysql_password}")
    
    print("\n⚠️  تحذير مهم:")
    print("- احتفظ بهذه القيم في مكان آمن")
    print("- لا تشارك ملف .env مع أحد")
    print("- لا ترفع ملف .env على Git")
    
    return True

if __name__ == "__main__":
    # التحقق من وجود ملف .env
    if os.path.exists('.env'):
        response = input("⚠️  ملف .env موجود بالفعل. هل تريد استبداله؟ (y/N): ")
        if response.lower() not in ['y', 'yes', 'نعم']:
            print("تم إلغاء العملية.")
            exit()
    
    create_env_file()