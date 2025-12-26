# دليل إعداد ملف البيئة (.env)

## ما هو ملف .env؟

ملف `.env` يحتوي على **متغيرات البيئة** الحساسة التي يحتاجها التطبيق للعمل بأمان. هذه المتغيرات تشمل كلمات المرور والمفاتيح السرية.

## لماذا يجب تغيير القيم؟

القيم الافتراضية في `.env.example` هي أمثلة فقط وليست آمنة. **يجب تغييرها** لحماية تطبيقك من:
- اختراق الجلسات
- الوصول غير المصرح لقاعدة البيانات
- سرقة البيانات المشفرة

## المتغيرات المطلوب تعديلها:

### 1. SECRET_KEY
```bash
SECRET_KEY=your-very-secure-secret-key-here
```
- **الغرض**: تشفير الجلسات وحماية النماذج
- **المطلوب**: نص عشوائي طويل (32-64 حرف)
- **مثال آمن**: `SECRET_KEY=a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0u1V2w3X4y5Z6`

### 2. DB_ENCRYPTION_KEY
```bash
DB_ENCRYPTION_KEY=your-database-encryption-key-here
```
- **الغرض**: تشفير البيانات الحساسة في قاعدة البيانات
- **المطلوب**: نص عشوائي (32 حرف بالضبط)
- **مثال آمن**: `DB_ENCRYPTION_KEY=x1Y2z3A4b5C6d7E8f9G0h1I2j3K4l5M6`

### 3. MYSQL_ROOT_PASSWORD
```bash
MYSQL_ROOT_PASSWORD=your-mysql-root-password-here
```
- **الغرض**: كلمة مرور مدير قاعدة البيانات
- **المطلوب**: كلمة مرور قوية (12+ حرف)
- **مثال آمن**: `MYSQL_ROOT_PASSWORD=MyStr0ng_DB_P@ssw0rd_2024!`

## طرق إنشاء ملف .env:

### الطريقة الأولى: التوليد التلقائي (مُوصى بها)

```bash
# تشغيل سكريبت التوليد التلقائي
python3 generate_env.py
```

**المميزات**:
- ✅ قيم آمنة تلقائياً
- ✅ لا حاجة للتفكير في القيم
- ✅ مفاتيح قوية ومعقدة

### الطريقة الثانية: التعديل اليدوي

```bash
# نسخ الملف المثال
cp .env.example .env

# تعديل الملف
nano .env
```

**خطوات التعديل**:
1. افتح الملف بمحرر النصوص
2. غير كل قيمة بقيمة آمنة
3. احفظ الملف

### الطريقة الثالثة: استخدام أدوات التوليد

```bash
# توليد مفتاح آمن باستخدام openssl
openssl rand -hex 32

# أو باستخدام Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## مثال على ملف .env آمن:

```bash
# ملف البيئة - قيم آمنة
SECRET_KEY=a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8s9T0u1V2w3X4y5Z6a1B2c3D4e5F6
DB_ENCRYPTION_KEY=x1Y2z3A4b5C6d7E8f9G0h1I2j3K4l5M6
MYSQL_ROOT_PASSWORD=MyStr0ng_DB_P@ssw0rd_2024!

# إعدادات الإنتاج
FLASK_ENV=production
```

## نصائح أمنية مهمة:

### ✅ افعل:
- استخدم قيم عشوائية ومعقدة
- احتفظ بنسخة احتياطية آمنة من كلمات المرور
- غير كلمات المرور بانتظام
- استخدم مدير كلمات مرور

### ❌ لا تفعل:
- لا تستخدم القيم الافتراضية
- لا تشارك ملف .env مع أحد
- لا ترفع ملف .env على Git
- لا تستخدم كلمات مرور بسيطة

## استكشاف الأخطاء:

### خطأ: "SECRET_KEY not set"
```bash
# تأكد من وجود ملف .env
ls -la .env

# تأكد من وجود SECRET_KEY في الملف
grep SECRET_KEY .env
```

### خطأ: "Database connection failed"
```bash
# تأكد من صحة كلمة مرور قاعدة البيانات
grep MYSQL_ROOT_PASSWORD .env
```

### خطأ: "Encryption key invalid"
```bash
# تأكد من أن مفتاح التشفير 32 حرف بالضبط
python3 -c "
with open('.env') as f:
    for line in f:
        if 'DB_ENCRYPTION_KEY' in line:
            key = line.split('=')[1].strip()
            print(f'Key length: {len(key)}')
            if len(key) != 32:
                print('❌ Key must be exactly 32 characters')
            else:
                print('✅ Key length is correct')
"
```

## التحقق من صحة الإعداد:

```bash
# تشغيل سكريبت التحقق
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = ['SECRET_KEY', 'DB_ENCRYPTION_KEY', 'MYSQL_ROOT_PASSWORD']
missing = []

for var in required_vars:
    value = os.getenv(var)
    if not value or value.startswith('your-'):
        missing.append(var)
    else:
        print(f'✅ {var}: Set correctly')

if missing:
    print(f'❌ Missing or invalid: {missing}')
else:
    print('✅ All environment variables are set correctly!')
"
```