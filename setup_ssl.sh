#!/bin/bash

# سكريبت إعداد SSL مع Let's Encrypt

echo "🔒 إعداد SSL مع Let's Encrypt..."

# متغيرات (غير هذه القيم)
DOMAIN="your-domain.com"
SUBDOMAIN="reports"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"
EMAIL="your-email@example.com"  # غير هذا إلى إيميلك

echo "📧 الإيميل: $EMAIL"
echo "🌐 الدومين: $FULL_DOMAIN"

# تثبيت Certbot
echo "📦 تثبيت Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# إيقاف nginx إذا كان يعمل
echo "⏹️ إيقاف nginx المؤقت..."
sudo systemctl stop nginx 2>/dev/null || true

# الحصول على شهادة SSL
echo "🔐 الحصول على شهادة SSL..."
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $FULL_DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ تم الحصول على شهادة SSL بنجاح!"
    
    # إعداد التجديد التلقائي
    echo "🔄 إعداد التجديد التلقائي..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker-compose -f /root/DRS/docker-compose.production.yml restart nginx'") | crontab -
    
    echo "✅ تم إعداد التجديد التلقائي"
    
    # إنشاء سكريبت التشغيل
    cat > deploy_with_ssl.sh << 'EOF'
#!/bin/bash

echo "🚀 تشغيل المشروع مع SSL..."

# إيقاف الحاويات الحالية
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# تشغيل الإنتاج مع SSL
docker-compose -f docker-compose.production.yml up -d --build

# انتظار تشغيل الخدمات
echo "⏳ انتظار تشغيل الخدمات..."
sleep 30

# التحقق من حالة الخدمات
echo "📊 حالة الخدمات:"
docker-compose -f docker-compose.production.yml ps

echo "✅ تم تشغيل المشروع مع SSL!"
echo "🌐 يمكنك الوصول للتطبيق على: https://$FULL_DOMAIN"
EOF
    
    chmod +x deploy_with_ssl.sh
    echo "✅ تم إنشاء سكريبت deploy_with_ssl.sh"
    
else
    echo "❌ فشل في الحصول على شهادة SSL"
    echo "تأكد من:"
    echo "1. الدومين يشير إلى IP الخادم"
    echo "2. المنافذ 80 و 443 مفتوحة"
    echo "3. لا يوجد خدمات أخرى تستخدم هذه المنافذ"
fi

echo ""
echo "📋 ملاحظات مهمة:"
echo "1. تأكد من أن DNS يشير إلى IP الخادم"
echo "2. تأكد من فتح المنافذ 80 و 443"
echo "3. الشهادة ستتجدد تلقائياً كل 3 أشهر"