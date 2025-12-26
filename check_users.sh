#!/bin/bash

echo "🔍 فحص المستخدمين الموجودين..."

# فحص المستخدمين في قاعدة البيانات
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f'عدد المستخدمين الموجودين: {len(users)}')
    
    for user in users:
        print(f'- المستخدم: {user.username}, الاسم: {user.employee_name}, مدير: {user.is_admin}')
    
    if len(users) == 0:
        print('❌ لا يوجد مستخدمين في قاعدة البيانات')
    else:
        print('✅ يوجد مستخدمين في قاعدة البيانات')
"