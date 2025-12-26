#!/bin/bash

echo "🔧 إصلاح إعدادات الدومين..."

# المتغيرات الصحيحة
DOMAIN="smart-sense.site"
SUBDOMAIN="drs"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"
EMAIL="a7medtarek002@gmail.com"

echo "📋 الإعدادات الصحيحة:"
echo "الدومين الرئيسي: $DOMAIN"
echo "الـ subdomain: $SUBDOMAIN"
echo "الدومين الكامل: $FULL_DOMAIN"
echo "الإيميل: $EMAIL"

# إنشاء ملف nginx محدث
echo "🔧 إنشاء ملف nginx محدث..."
cat > nginx_domain.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:5000;
    }

    # إعدادات الأمان
    server_tokens off;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # ضغط الملفات
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # إعادة توجيه HTTP إلى HTTPS
    server {
        listen 80;
        server_name ${FULL_DOMAIN};
        
        # إعادة توجيه إلى HTTPS
        return 301 https://\$server_name\$request_uri;
    }

    # إعدادات HTTPS
    server {
        listen 443 ssl http2;
        server_name ${FULL_DOMAIN};

        # شهادات SSL
        ssl_certificate /etc/letsencrypt/live/${FULL_DOMAIN}/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/${FULL_DOMAIN}/privkey.pem;

        # إعدادات SSL الآمنة
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # HSTS
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header X-Forwarded-Host \$server_name;
            
            # إعدادات إضافية للتطبيقات
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # ملفات ثابتة مع تخزين مؤقت
        location /static {
            proxy_pass http://app;
            proxy_set_header Host \$host;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

echo "✅ تم إنشاء ملف nginx_domain.conf محدث"

# إنشاء docker-compose للإنتاج
echo "🔧 إنشاء ملف docker-compose.production.yml محدث..."
cat > docker-compose.production.yml << EOF
version: '3.8'

services:
  web:
    build: .
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=\${SECRET_KEY}
      - DB_ENCRYPTION_KEY=\${DB_ENCRYPTION_KEY}
      - DATABASE_URL=mysql+pymysql://root:\${MYSQL_ROOT_PASSWORD}@db:3306/daily_report
    depends_on:
      - db
    volumes:
      - ./instance:/app/instance
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=\${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=daily_report
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx_domain.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

volumes:
  mysql_data:

networks:
  app-network:
    driver: bridge
EOF

echo "✅ تم إنشاء ملف docker-compose.production.yml محدث"

# الحصول على شهادة SSL
echo "🔐 الحصول على شهادة SSL..."

# إيقاف nginx إذا كان يعمل
sudo systemctl stop nginx 2>/dev/null || true

# الحصول على شهادة SSL
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
    cat > deploy_with_ssl.sh << 'EOFSCRIPT'
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
echo "🌐 يمكنك الوصول للتطبيق على: https://drs.smart-sense.site"
EOFSCRIPT
    
    chmod +x deploy_with_ssl.sh
    echo "✅ تم إنشاء سكريبت deploy_with_ssl.sh"
    
    echo ""
    echo "🎉 تم الإعداد بنجاح!"
    echo "🌐 الدومين: https://$FULL_DOMAIN"
    echo "📋 الخطوة التالية: شغل ./deploy_with_ssl.sh"
    
else
    echo "❌ فشل في الحصول على شهادة SSL"
    echo "تأكد من:"
    echo "1. DNS يشير إلى IP الخادم: $FULL_DOMAIN"
    echo "2. المنافذ 80 و 443 مفتوحة"
    echo "3. لا يوجد خدمات أخرى تستخدم هذه المنافذ"
fi