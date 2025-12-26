#!/bin/bash

echo "🔄 إعادة بناء الحاوية وإنشاء المستخدمين..."

# إيقاف الحاويات
echo "⏹️ إيقاف الحاويات..."
docker-compose -f docker-compose.simple.yml down

# إعادة بناء الحاوية مع الملفات الجديدة
echo "🔨 إعادة بناء الحاوية..."
docker-compose -f docker-compose.simple.yml build --no-cache

# تشغيل الحاويات
echo "▶️ تشغيل الحاويات..."
docker-compose -f docker-compose.simple.yml up -d

# انتظار تشغيل قاعدة البيانات
echo "⏳ انتظار تشغيل قاعدة البيانات..."
sleep 30

# إنشاء الجداول
echo "🗄️ إنشاء الجداول..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('تم إنشاء الجداول')
"

# إنشاء المستخدمين باستخدام الملف الجديد
echo "👥 إنشاء المستخدمين..."
docker-compose -f docker-compose.simple.yml exec web python create_users_manual.py

echo "✅ تم الانتهاء!"