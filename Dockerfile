# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تعيين متغير البيئة لمنع إنشاء ملفات .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تعيين مجلد العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY . .

# إنشاء مجلد instance إذا لم يكن موجوداً
RUN mkdir -p instance

# إنشاء مستخدم غير root لتشغيل التطبيق
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# تعريض المنفذ
EXPOSE 5000

# تشغيل التطبيق
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:application"]