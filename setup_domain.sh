#!/bin/bash

# سكريبت إعداد الدومين والـ subdomain

echo "🌐 إعداد الدومين والـ subdomain..."

# متغيرات الدومين (غير هذه القيم)
DOMAIN="your-domain.com"  # غير هذا إلى الدومين الخاص بك
SUBDOMAIN="reports"       # غير هذا إلى الـ subdomain المطلوب
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "📋 إعداد الدومين:"
echo "الدومين الرئيسي: $DOMAIN"
echo "الـ subdomain: $SUBDOMAIN"
echo "الدومين الكامل: $FULL_DOMAIN"

# إنشاء ملف nginx محدث للدومين
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

        # شهادات SSL (سيتم إنشاؤها بـ Let's Encrypt)
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

echo "✅ تم إنشاء ملف nginx_domain.conf"

# إنشاء docker-compose للإنتاج مع nginx
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

echo "✅ تم إنشاء ملف docker-compose.production.yml"

echo ""
echo "📋 الخطوات التالية:"
echo "1. غير قيم DOMAIN و SUBDOMAIN في هذا الملف"
echo "2. أشر الـ DNS للدومين إلى IP الخادم"
echo "3. شغل سكريبت إعداد SSL"
echo "4. شغل المشروع بالإعدادات الجديدة"