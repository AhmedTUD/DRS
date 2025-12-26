#!/bin/bash

echo "🔍 تشخيص مشكلة تسجيل الدخول..."

docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app
from app.models import User
from werkzeug.security import check_password_hash
from flask import url_for

app = create_app()

print('🔍 اختبار تسجيل الدخول خطوة بخطوة...')

with app.app_context():
    # اختبار url_for
    try:
        admin_url = url_for('admin.dashboard')
        employee_url = url_for('employee.dashboard')
        print(f'✅ admin.dashboard URL: {admin_url}')
        print(f'✅ employee.dashboard URL: {employee_url}')
    except Exception as e:
        print(f'❌ خطأ في url_for: {e}')
    
    # اختبار المستخدمين
    admin = User.query.filter_by(username='admin').first()
    employee = User.query.filter_by(username='employee').first()
    
    if admin:
        print(f'✅ المدير موجود: {admin.username}, is_admin: {admin.is_admin}')
    else:
        print('❌ المدير غير موجود')
        
    if employee:
        print(f'✅ الموظف موجود: {employee.username}, is_admin: {employee.is_admin}')
    else:
        print('❌ الموظف غير موجود')

print('')
print('🧪 محاكاة تسجيل الدخول الكاملة...')

with app.test_client() as client:
    # محاولة تسجيل دخول المدير
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)
    
    print(f'📊 نتيجة تسجيل دخول المدير:')
    print(f'   Status Code: {response.status_code}')
    
    if response.status_code == 302:
        print(f'   إعادة توجيه إلى: {response.location}')
        print('   ✅ تسجيل الدخول نجح!')
        
        # اتباع إعادة التوجيه
        redirect_response = client.get(response.location)
        print(f'   Status Code للصفحة المُوجه إليها: {redirect_response.status_code}')
        
        if redirect_response.status_code == 200:
            print('   ✅ الوصول للوحة التحكم نجح!')
        else:
            print('   ❌ مشكلة في الوصول للوحة التحكم')
            
    elif response.status_code == 200:
        print('   ❌ تسجيل الدخول فشل - عاد لنفس الصفحة')
        # فحص محتوى الاستجابة للبحث عن رسائل خطأ
        content = response.data.decode()
        if 'Invalid username or password' in content:
            print('   رسالة خطأ موجودة في المحتوى')
        else:
            print('   لا توجد رسالة خطأ - مشكلة أخرى')
    else:
        print(f'   ❌ خطأ غير متوقع: {response.status_code}')
"