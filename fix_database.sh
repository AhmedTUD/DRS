#!/bin/bash

echo "🔧 إصلاح مشكلة قاعدة البيانات..."

# إيقاف الحاويات
echo "⏹️ إيقاف الحاويات..."
docker-compose -f docker-compose.simple.yml down -v

# حذف البيانات القديمة
echo "🧹 حذف البيانات القديمة..."
docker volume rm drs_mysql_data 2>/dev/null || true

# إعادة تشغيل الحاويات
echo "🚀 إعادة تشغيل الحاويات..."
docker-compose -f docker-compose.simple.yml up -d --build

# انتظار تشغيل قاعدة البيانات
echo "⏳ انتظار تشغيل قاعدة البيانات..."
sleep 45

# محاولة الاتصال بقاعدة البيانات
echo "🔍 اختبار الاتصال بقاعدة البيانات..."
docker-compose -f docker-compose.simple.yml exec db mysql -u root -p$(grep MYSQL_ROOT_PASSWORD .env | cut -d '=' -f2) -e "SELECT 1;" 2>/dev/null && echo "✅ قاعدة البيانات تعمل" || echo "❌ مشكلة في قاعدة البيانات"

# إنشاء الجداول
echo "🗄️ إنشاء الجداول..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('✅ تم إنشاء الجداول بنجاح')
    except Exception as e:
        print(f'❌ خطأ في إنشاء الجداول: {e}')
"

# إنشاء المستخدمين التجريبيين
echo "👥 إنشاء المستخدمين التجريبيين..."
docker-compose -f docker-compose.simple.yml exec web python create_demo_users.py

echo "✅ تم إصلاح قاعدة البيانات!"