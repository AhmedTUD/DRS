# التشغيل السريع باستخدام Docker

## خطوات سريعة للتشغيل على VPS

### 1. تثبيت Docker (Ubuntu/Debian)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. تثبيت Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. رفع المشروع
```bash
# رفع الملفات إلى VPS أو استنساخ من Git
git clone <your-repo-url>
cd <project-folder>
```

### 4. إعداد البيئة

#### الطريقة الأولى: التوليد التلقائي (مُوصى بها)
```bash
python3 generate_env.py
```

#### الطريقة الثانية: التعديل اليدوي
```bash
cp .env.example .env
nano .env  # عدل القيم التالية:
# SECRET_KEY=مفتاح-آمن-طويل-64-حرف
# DB_ENCRYPTION_KEY=مفتاح-تشفير-32-حرف  
# MYSQL_ROOT_PASSWORD=كلمة-مرور-قوية
```

### 5. تشغيل المشروع
```bash
chmod +x deploy.sh
./deploy.sh
```

### 6. التحقق من التشغيل
```bash
docker-compose ps
curl http://localhost:5000
```

## أوامر مهمة

- **إيقاف**: `docker-compose down`
- **تشغيل**: `docker-compose up -d`
- **السجلات**: `docker-compose logs -f`
- **إعادة بناء**: `docker-compose build --no-cache`

## الوصول للتطبيق
- محلياً: `http://localhost:5000`
- على VPS: `http://your-server-ip:5000`