#!/bin/bash

echo "🔍 اختبار تسجيل الدخول التفصيلي..."

# اختبار تسجيل الدخول مع تفاصيل أكثر
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    print('🔍 فحص المستخدمين في قاعدة البيانات:')
    users = User.query.all()
    print(f'عدد المستخدمين: {len(users)}')
    
    for user in users:
        print(f'المستخدم: {user.username}')
        print(f'  - الاسم: {user.employee_name}')
        print(f'  - كود الموظف: {user.employee_code}')
        print(f'  - مدير: {user.is_admin}')
        print(f'  - تاريخ الإنشاء: {user.created_at}')
        print(f'  - hash كلمة المرور: {user.password_hash[:50]}...')
        
        # اختبار كلمة المرور
        if user.username == 'admin':
            test_pass = check_password_hash(user.password_hash, 'admin123')
            print(f'  - اختبار كلمة المرور admin123: {\"✅ صحيح\" if test_pass else \"❌ خطأ\"}')
        elif user.username == 'employee':
            test_pass = check_password_hash(user.password_hash, 'employee123')
            print(f'  - اختبار كلمة المرور employee123: {\"✅ صحيح\" if test_pass else \"❌ خطأ\"}')
        print('---')
"

echo ""
echo "🌐 اختبار الوصول للتطبيق:"
echo "الرابط الصحيح لتسجيل الدخول: http://your-server-ip:5000/auth/login"
echo ""
echo "📋 جرب هذه الروابط:"
echo "- الصفحة الرئيسية: http://your-server-ip:5000/"
echo "- تسجيل الدخول: http://your-server-ip:5000/auth/login"

# اختبار curl للتطبيق
echo ""
echo "🧪 اختبار HTTP:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5000/ || echo "❌ لا يمكن الوصول للتطبيق"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5000/auth/login || echo "❌ لا يمكن الوصول لصفحة تسجيل الدخول"