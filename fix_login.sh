#!/bin/bash

echo "🔧 إصلاح مشكلة تسجيل الدخول..."

# 1. فحص المستخدمين الحاليين
echo "🔍 فحص المستخدمين الحاليين..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f'عدد المستخدمين: {len(users)}')
    for user in users:
        print(f'- {user.username}: {user.employee_name}')
"

# 2. إنشاء المستخدمين يدوياً
echo ""
echo "👥 إنشاء المستخدمين يدوياً..."
docker-compose -f docker-compose.simple.yml exec web python create_users_manual.py

# 3. اختبار تسجيل الدخول
echo ""
echo "🧪 اختبار تسجيل الدخول..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    # اختبار المدير
    admin = User.query.filter_by(username='admin').first()
    if admin:
        if check_password_hash(admin.password_hash, 'admin123'):
            print('✅ تسجيل دخول المدير يعمل')
        else:
            print('❌ كلمة مرور المدير خاطئة')
    else:
        print('❌ المدير غير موجود')
    
    # اختبار الموظف
    employee = User.query.filter_by(username='employee').first()
    if employee:
        if check_password_hash(employee.password_hash, 'employee123'):
            print('✅ تسجيل دخول الموظف يعمل')
        else:
            print('❌ كلمة مرور الموظف خاطئة')
    else:
        print('❌ الموظف غير موجود')
"

echo ""
echo "✅ تم إصلاح مشكلة تسجيل الدخول!"
echo ""
echo "🔐 بيانات تسجيل الدخول:"
echo "المدير: admin / admin123"
echo "الموظف: employee / employee123"