#!/bin/bash

echo "🧪 اختبار التطبيق..."

# الحصول على IP الخادم
SERVER_IP=$(curl -s ifconfig.me)

echo "🌐 معلومات الخادم:"
echo "IP الخادم: $SERVER_IP"
echo "رابط التطبيق: http://$SERVER_IP:5000"

# اختبار الاتصال بالتطبيق
echo ""
echo "🔍 اختبار الاتصال بالتطبيق..."
if curl -f -s http://localhost:5000 > /dev/null; then
    echo "✅ التطبيق يعمل بشكل طبيعي"
    echo "🎉 يمكنك الوصول للتطبيق على: http://$SERVER_IP:5000"
else
    echo "❌ مشكلة في التطبيق"
    echo "📝 السجلات:"
    docker-compose -f docker-compose.simple.yml logs --tail=20 web
fi

# عرض حالة الحاويات
echo ""
echo "📊 حالة الحاويات:"
docker-compose -f docker-compose.simple.yml ps

# اختبار قاعدة البيانات
echo ""
echo "🗄️ اختبار قاعدة البيانات:"
MYSQL_PASSWORD=$(grep MYSQL_ROOT_PASSWORD .env | cut -d '=' -f2)
docker-compose -f docker-compose.simple.yml exec db mysql -u root -p$MYSQL_PASSWORD -e "SHOW DATABASES;" 2>/dev/null && echo "✅ قاعدة البيانات تعمل" || echo "❌ مشكلة في قاعدة البيانات"

echo ""
echo "🔐 بيانات تسجيل الدخول التجريبية:"
echo "المدير: admin@example.com / admin123"
echo "الموظف: employee@example.com / emp123"