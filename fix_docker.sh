#!/bin/bash

echo "🔧 إصلاح مشاكل Docker..."

# تحديث Docker إلى أحدث إصدار
echo "📦 تحديث Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تحديث Docker Compose إلى أحدث إصدار
echo "📦 تحديث Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# إعادة تشغيل Docker
echo "🔄 إعادة تشغيل Docker..."
sudo systemctl restart docker

# التحقق من الإصدارات
echo "✅ التحقق من الإصدارات:"
docker --version
docker-compose --version

echo "✅ تم تحديث Docker بنجاح!"