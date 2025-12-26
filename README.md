# نظام التقارير اليومية - Daily Report System

نظام إدارة التقارير اليومية للموظفين مبني بـ Flask مع دعم Docker للنشر السهل.

## المميزات

- 🔐 نظام مصادقة آمن للمستخدمين
- 👥 إدارة المستخدمين (مدير/موظف)
- 📊 إنشاء وإدارة التقارير اليومية
- 📈 تصدير التقارير بصيغ مختلفة
- 🔒 تشفير البيانات الحساسة
- 🐳 دعم Docker للنشر السهل
- 🌐 واجهة مستخدم عربية

## التقنيات المستخدمة

- **Backend**: Flask, SQLAlchemy, MySQL/SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: MySQL (للإنتاج), SQLite (للتطوير)
- **Security**: تشفير البيانات, CSRF Protection, Rate Limiting
- **Deployment**: Docker, Docker Compose, Nginx

## التشغيل السريع باستخدام Docker

### 1. تثبيت Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. استنساخ المشروع
```bash
git clone https://github.com/AhmedTUD/DRS.git
cd DRS
```

### 3. إعداد البيئة
```bash
cp .env.example .env
nano .env  # عدل القيم المطلوبة
```

### 4. تشغيل المشروع
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. الوصول للتطبيق
- محلياً: http://localhost:5000
- على الخادم: http://your-server-ip:5000

## التشغيل المحلي (بدون Docker)

### 1. إعداد البيئة الافتراضية
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. إعداد قاعدة البيانات
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 4. تشغيل التطبيق
```bash
python app.py
```

## إعداد المستخدمين الأوليين

```bash
python create_demo_users.py
```

سيتم إنشاء:
- مدير: admin@example.com / admin123
- موظف: employee@example.com / emp123

## الأدلة والوثائق

- [دليل Docker الشامل](DOCKER_SETUP_GUIDE.md)
- [التشغيل السريع](QUICK_START.md)
- [دليل الأمان](SECURITY_GUIDE.md)

## الأوامر المفيدة

### Docker
```bash
# عرض حالة الحاويات
docker-compose ps

# عرض السجلات
docker-compose logs -f

# إعادة تشغيل
docker-compose restart

# إيقاف
docker-compose down

# تحديث
git pull && docker-compose build --no-cache && docker-compose up -d
```

### النسخ الاحتياطي
```bash
# نسخ احتياطي لقاعدة البيانات
docker-compose exec db mysqldump -u root -p daily_report > backup.sql

# استعادة النسخة الاحتياطية
docker-compose exec -T db mysql -u root -p daily_report < backup.sql
```

## الأمان

- تشفير كلمات المرور باستخدام bcrypt
- تشفير البيانات الحساسة في قاعدة البيانات
- حماية CSRF
- تحديد معدل الطلبات (Rate Limiting)
- رؤوس الأمان HTTP
- جلسات آمنة

## المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push للفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## الدعم

إذا واجهت أي مشاكل أو لديك أسئلة، يرجى فتح issue في GitHub.

## لقطات الشاشة

### لوحة تحكم المدير
![Admin Dashboard](screenshots/admin-dashboard.png)

### لوحة تحكم الموظف
![Employee Dashboard](screenshots/employee-dashboard.png)

### إنشاء تقرير
![Create Report](screenshots/create-report.png)

---

تم تطوير هذا المشروع بـ ❤️ لتسهيل إدارة التقارير اليومية