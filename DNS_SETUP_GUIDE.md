# دليل إعداد DNS والدومين

## 1. إعداد DNS Records

### في لوحة تحكم الدومين الخاص بك، أضف:

#### A Record للـ Subdomain:
```
Type: A
Name: reports (أو أي اسم تريده للـ subdomain)
Value: IP_ADDRESS_OF_YOUR_VPS
TTL: 300 (أو أقل قيمة متاحة)
```

#### مثال:
```
reports.yourdomain.com → 123.456.789.123
```

## 2. التحقق من DNS

### من جهازك المحلي:
```bash
# التحقق من A record
nslookup reports.yourdomain.com

# أو باستخدام dig
dig reports.yourdomain.com A
```

### من VPS:
```bash
# التحقق من الوصول للدومين
ping reports.yourdomain.com
```

## 3. إعداد المشروع

### 1. تحديث ملفات الإعداد:
```bash
# تعديل setup_domain.sh
nano setup_domain.sh

# غير هذه القيم:
DOMAIN="yourdomain.com"      # الدومين الخاص بك
SUBDOMAIN="reports"          # اسم الـ subdomain
```

### 2. تعديل setup_ssl.sh:
```bash
nano setup_ssl.sh

# غير هذه القيم:
DOMAIN="yourdomain.com"
SUBDOMAIN="reports"
EMAIL="your-email@example.com"  # إيميلك للتنبيهات
```

## 4. تشغيل الإعداد

### 1. إعداد الدومين:
```bash
chmod +x setup_domain.sh
./setup_domain.sh
```

### 2. إعداد SSL:
```bash
chmod +x setup_ssl.sh
./setup_ssl.sh
```

### 3. تشغيل المشروع:
```bash
./deploy_with_ssl.sh
```

## 5. اختبار الإعداد

### تحقق من:
- ✅ HTTP يعيد توجيه إلى HTTPS
- ✅ HTTPS يعمل بشكل صحيح
- ✅ PWA يعمل (بسبب HTTPS)
- ✅ شهادة SSL صالحة

### أوامر الاختبار:
```bash
# اختبار HTTP (يجب أن يعيد توجيه)
curl -I http://reports.yourdomain.com

# اختبار HTTPS
curl -I https://reports.yourdomain.com

# اختبار شهادة SSL
openssl s_client -connect reports.yourdomain.com:443 -servername reports.yourdomain.com
```

## 6. إدارة المشاريع المتعددة

### لإضافة مشاريع أخرى:

#### 1. إنشاء subdomains إضافية:
```
api.yourdomain.com    → مشروع API
blog.yourdomain.com   → مدونة
shop.yourdomain.com   → متجر إلكتروني
```

#### 2. استخدام Nginx كـ Reverse Proxy:
```nginx
# في ملف nginx رئيسي
server {
    listen 443 ssl;
    server_name reports.yourdomain.com;
    # إعدادات مشروع التقارير
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    # إعدادات مشروع API
}
```

## 7. مراقبة وصيانة

### تجديد الشهادات:
```bash
# التحقق من حالة الشهادات
sudo certbot certificates

# تجديد يدوي (إذا احتجت)
sudo certbot renew

# اختبار التجديد
sudo certbot renew --dry-run
```

### مراقبة الخدمات:
```bash
# حالة Docker
docker-compose -f docker-compose.production.yml ps

# سجلات nginx
docker-compose -f docker-compose.production.yml logs nginx

# سجلات التطبيق
docker-compose -f docker-compose.production.yml logs web
```

## 8. استكشاف الأخطاء

### مشاكل شائعة:

#### DNS لا يعمل:
- تحقق من A record
- انتظر انتشار DNS (قد يستغرق ساعات)
- استخدم أدوات مثل whatsmydns.net

#### SSL لا يعمل:
- تحقق من فتح المنافذ 80 و 443
- تأكد من عدم وجود خدمات أخرى على هذه المنافذ
- تحقق من صحة DNS

#### PWA لا يعمل:
- تأكد من HTTPS يعمل
- تحقق من Service Worker في Developer Tools
- امسح cache المتصفح

## 9. نصائح الأمان

### 1. جدار الحماية:
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. تحديثات النظام:
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. مراقبة السجلات:
```bash
# مراقبة محاولات الوصول
sudo tail -f /var/log/nginx/access.log

# مراقبة الأخطاء
sudo tail -f /var/log/nginx/error.log
```

## 10. النسخ الاحتياطي

### نسخ احتياطي لقاعدة البيانات:
```bash
docker-compose -f docker-compose.production.yml exec db mysqldump -u root -p daily_report > backup_$(date +%Y%m%d).sql
```

### نسخ احتياطي للملفات:
```bash
tar -czf backup_files_$(date +%Y%m%d).tar.gz /root/DRS
```