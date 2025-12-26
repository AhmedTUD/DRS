#!/bin/bash

echo "🚀 النشر المبسط..."

# التحقق من ملف .env
if [ ! -f .env ]; then
    echo "❌ ملف .env غير موجود. إنشاء ملف جديد..."
    python3 generate_env.py
fi

# عرض محتوى ملف .env للتأكد
echo "📋 محتوى ملف .env:"
cat .env
echo ""

# إيقاف الحاويات الحالية
echo "⏹️ إيقاف الحاويات الحالية..."
docker-compose -f docker-compose.simple.yml down

# بناء وتشغيل الحاويات
echo "🔨 بناء وتشغيل الحاويات..."
docker-compose -f docker-compose.simple.yml up -d --build

# انتظار تشغيل قاعدة البيانات
echo "⏳ انتظار تشغيل قاعدة البيانات..."
sleep 30

# تشغيل migrations
echo "🗄️ إعداد قاعدة البيانات..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('تم إنشاء الجداول بنجاح')
"

# عرض حالة الحاويات
echo "📊 حالة الحاويات:"
docker-compose -f docker-compose.simple.yml ps

# عرض السجلات
echo "📝 آخر السجلات:"
docker-compose -f docker-compose.simple.yml logs --tail=10

echo "✅ تم النشر بنجاح!"
echo "🌐 يمكنك الوصول للتطبيق على: http://$(curl -s ifconfig.me):5000"