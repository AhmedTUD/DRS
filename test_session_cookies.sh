#!/bin/bash

echo "🍪 اختبار الجلسة والكوكيز..."

# اختبار إعدادات الجلسة
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app
import os

app = create_app()
print('🔍 إعدادات الجلسة:')
print(f'SESSION_COOKIE_SECURE: {app.config.get(\"SESSION_COOKIE_SECURE\")}')
print(f'SESSION_COOKIE_HTTPONLY: {app.config.get(\"SESSION_COOKIE_HTTPONLY\")}')
print(f'SESSION_COOKIE_SAMESITE: {app.config.get(\"SESSION_COOKIE_SAMESITE\")}')
print(f'SECRET_KEY موجود: {bool(app.config.get(\"SECRET_KEY\"))}')
print(f'FLASK_ENV: {os.environ.get(\"FLASK_ENV\", \"development\")}')
"

echo ""
echo "🧪 اختبار تسجيل الدخول مع الكوكيز:"

# اختبار تسجيل الدخول مع تتبع الكوكيز
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app

app = create_app()

print('🔐 اختبار تسجيل الدخول مع الكوكيز...')

with app.test_client() as client:
    # محاولة تسجيل الدخول
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 302:
        print(f'إعادة توجيه إلى: {response.location}')
        
        # فحص الكوكيز
        cookies = response.headers.getlist('Set-Cookie')
        print(f'عدد الكوكيز: {len(cookies)}')
        for cookie in cookies:
            print(f'Cookie: {cookie}')
        
        # محاولة الوصول للصفحة المحمية
        protected_response = client.get('/admin/dashboard')
        print(f'الوصول للوحة التحكم: {protected_response.status_code}')
        
        if protected_response.status_code == 200:
            print('✅ الجلسة تعمل بشكل صحيح!')
        else:
            print('❌ مشكلة في الجلسة')
    else:
        print('❌ تسجيل الدخول فشل')
"