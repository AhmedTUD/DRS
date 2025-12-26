# دليل تثبيت وتشغيل المشروع باستخدام Docker على VPS

## 1. تثبيت Docker على VPS Linux

### Ubuntu/Debian:
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# إضافة مفتاح Docker GPG
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# إضافة مستودع Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# تثبيت Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# إضافة المستخدم الحالي لمجموعة docker
sudo usermod -aG docker $USER

# إعادة تسجيل الدخول أو تشغيل:
newgrp docker
```

### CentOS/RHEL:
```bash
# تثبيت Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# تشغيل Docker
sudo systemctl start docker
sudo systemctl enable docker

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 2. رفع المشروع على VPS

### الطريقة الأولى: Git Clone
```bash
# استنساخ المشروع
git clone <repository-url>
cd <project-name>
```

### الطريقة الثانية: رفع الملفات يدوياً
```bash
# إنشاء مجلد المشروع
mkdir daily-report-system
cd daily-report-system

# رفع الملفات باستخدام scp أو rsync
scp -r /path/to/local/project/* user@server-ip:/path/to/project/
```

## 3. إعداد متغيرات البيئة

```bash
# نسخ ملف البيئة
cp .env.example .env

# تعديل ملف البيئة
nano .env
```

قم بتعديل القيم التالية في ملف `.env`:
```
SECRET_KEY=your-very-secure-secret-key-here-32-characters-long
DB_ENCRYPTION_KEY=your-database-encryption-key-here-32-chars
MYSQL_ROOT_PASSWORD=your-strong-mysql-password-here
```

## 4. تشغيل المشروع

```bash
# جعل سكريبت النشر قابل للتنفيذ
chmod +x deploy.sh

# تشغيل سكريبت النشر
./deploy.sh
```

أو يدوياً:
```bash
# بناء وتشغيل الحاويات
docker-compose up -d --build

# التحقق من حالة الحاويات
docker-compose ps

# عرض السجلات
docker-compose logs -f
```

## 5. إعداد Nginx (اختياري للإنتاج)

إذا كنت تريد استخدام اسم نطاق:

```bash
# تعديل ملف nginx.conf
nano nginx.conf

# غير "your-domain.com" إلى اسم النطاق الخاص بك
```

## 6. إعداد SSL مع Let's Encrypt (اختياري)

```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com

# تجديد تلقائي للشهادة
sudo crontab -e
# أضف السطر التالي:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 7. أوامر مفيدة للإدارة

```bash
# عرض حالة الحاويات
docker-compose ps

# عرض السجلات
docker-compose logs -f web

# إعادة تشغيل خدمة معينة
docker-compose restart web

# تحديث التطبيق
git pull
docker-compose build --no-cache
docker-compose up -d

# إيقاف جميع الخدمات
docker-compose down

# إيقاف وحذف البيانات
docker-compose down -v

# الدخول إلى حاوية التطبيق
docker-compose exec web bash

# تشغيل أوامر Flask
docker-compose exec web python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 8. استكشاف الأخطاء

### مشكلة في الاتصال بقاعدة البيانات:
```bash
# التحقق من سجلات قاعدة البيانات
docker-compose logs db

# إعادة تشغيل قاعدة البيانات
docker-compose restart db
```

### مشكلة في التطبيق:
```bash
# عرض سجلات التطبيق
docker-compose logs web

# الدخول إلى حاوية التطبيق للتشخيص
docker-compose exec web bash
```

### تحديث الكود:
```bash
# سحب آخر التحديثات
git pull

# إعادة بناء وتشغيل
docker-compose up -d --build
```

## 9. النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
docker-compose exec db mysqldump -u root -p daily_report > backup_$(date +%Y%m%d_%H%M%S).sql

# استعادة النسخة الاحتياطية
docker-compose exec -T db mysql -u root -p daily_report < backup_file.sql
```

## 10. مراقبة الأداء

```bash
# مراقبة استخدام الموارد
docker stats

# مراقبة مساحة القرص
docker system df

# تنظيف الملفات غير المستخدمة
docker system prune -a
```

## الأمان

1. تأكد من تغيير كلمات المرور الافتراضية
2. استخدم جدار حماية (UFW على Ubuntu)
3. قم بتحديث النظام بانتظام
4. استخدم شهادات SSL
5. راقب السجلات بانتظام

```bash
# تفعيل جدار الحماية
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
```