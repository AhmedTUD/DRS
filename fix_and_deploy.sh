#!/bin/bash

echo "🔧 إصلاح المشاكل وإعادة النشر..."

# 1. تحديث Docker
echo "📦 تحديث Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تحديث Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# إعادة تشغيل Docker
sudo systemctl restart docker

# 2. إنشاء ملف .env جديد بدون رموز خاصة
echo "🔐 إنشاء ملف .env جديد..."
python3 generate_env.py

# 3. التحقق من ملف .env
echo "📋 محتوى ملف .env:"
cat .env

# 4. تنظيف Docker
echo "🧹 تنظيف Docker..."
docker system prune -f

# 5. إعادة النشر
echo "🚀 إعادة النشر..."
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# 6. انتظار تشغيل الخدمات
echo "⏳ انتظار تشغيل الخدمات..."
sleep 30

# 7. التحقق من حالة الحاويات
echo "📊 حالة الحاويات:"
docker-compose ps

# 8. عرض السجلات
echo "📝 السجلات:"
docker-compose logs --tail=20

echo "✅ تم الإصلاح والنشر!"