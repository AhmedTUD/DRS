#!/bin/bash

echo "🔍 اختبار بسيط لصفحة تسجيل الدخول..."

# اختبار الوصول لصفحة تسجيل الدخول
echo "📄 فحص محتوى صفحة تسجيل الدخول:"
curl -s http://localhost:5000/auth/login | head -20

echo ""
echo "🌐 اختبار الروابط:"
echo "Status Code للصفحة الرئيسية:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/
echo ""

echo "Status Code لصفحة تسجيل الدخول:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/auth/login
echo ""

echo ""
echo "🔐 تأكد من استخدام هذه البيانات بالضبط:"
echo "اسم المستخدم: admin"
echo "كلمة المرور: admin123"
echo ""
echo "🌐 الرابط الصحيح:"
echo "http://[2a02:c207:2296:3003::1]:5000/auth/login"