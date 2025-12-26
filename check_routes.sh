#!/bin/bash

echo "🔍 فحص routes المتاحة في التطبيق..."

docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app

app = create_app()
with app.app_context():
    print('📋 Routes المتاحة:')
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f'{rule.endpoint:30} {methods:15} {rule.rule}')
"

echo ""
echo "🌐 الروابط المهمة:"
echo "- الصفحة الرئيسية: http://your-server-ip:5000/"
echo "- تسجيل الدخول: http://your-server-ip:5000/auth/login"
echo "- لوحة المدير: http://your-server-ip:5000/admin/dashboard"
echo "- لوحة الموظف: http://your-server-ip:5000/employee/dashboard"