#!/bin/bash

echo "🧪 محاكاة تسجيل الدخول..."

# محاكاة POST request لتسجيل الدخول
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()

# محاكاة تسجيل الدخول
print('🔐 محاكاة تسجيل دخول المدير...')
with app.test_client() as client:
    # GET صفحة تسجيل الدخول
    response = client.get('/auth/login')
    print(f'GET /auth/login: {response.status_code}')
    
    # POST بيانات تسجيل الدخول
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)
    
    print(f'POST /auth/login: {response.status_code}')
    if response.status_code == 302:
        print(f'إعادة توجيه إلى: {response.location}')
        print('✅ تسجيل الدخول نجح!')
    else:
        print('❌ تسجيل الدخول فشل')
        print(f'Response: {response.data.decode()[:200]}...')

print('')
print('🔐 محاكاة تسجيل دخول الموظف...')
with app.test_client() as client:
    response = client.post('/auth/login', data={
        'username': 'employee',
        'password': 'employee123'
    }, follow_redirects=False)
    
    print(f'POST /auth/login (employee): {response.status_code}')
    if response.status_code == 302:
        print(f'إعادة توجيه إلى: {response.location}')
        print('✅ تسجيل دخول الموظف نجح!')
    else:
        print('❌ تسجيل دخول الموظف فشل')
"

echo ""
echo "🌐 تأكد من استخدام الرابط الصحيح:"
echo "http://[2a02:c207:2296:3003::1]:5000/"
echo "أو"
echo "http://[2a02:c207:2296:3003::1]:5000/auth/login"