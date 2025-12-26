#!/bin/bash

# سكريبت نشر التطبيق على VPS
echo "🚀 بدء عملية النشر..."

# التحقق من وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker غير مثبت. يرجى تثبيت Docker أولاً"
    exit 1
fi

# التحقق من وجود Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose غير مثبت. يرجى تثبيت Docker Compose أولاً"
    exit 1
fi

# التحقق من وجود ملف .env
if [ ! -f .env ]; then
    echo "❌ ملف .env غير موجود. يرجى إنشاؤه من .env.example"
    echo "cp .env.example .env"
    echo "ثم قم بتعديل القيم في ملف .env"
    exit 1
fi

# إيقاف الحاويات الحالية
echo "⏹️ إيقاف الحاويات الحالية..."
docker-compose down

# بناء الصور الجديدة
echo "🔨 بناء الصور الجديدة..."
docker-compose build --no-cache

# تشغيل الحاويات
echo "▶️ تشغيل الحاويات..."
docker-compose up -d

# انتظار تشغيل قاعدة البيانات
echo "⏳ انتظار تشغيل قاعدة البيانات..."
sleep 30

# تشغيل migrations
echo "🗄️ تشغيل migrations..."
docker-compose exec web python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('تم إنشاء الجداول بنجاح')
"

# عرض حالة الحاويات
echo "📊 حالة الحاويات:"
docker-compose ps

echo "✅ تم النشر بنجاح!"
echo "🌐 يمكنك الوصول للتطبيق على: http://your-server-ip"