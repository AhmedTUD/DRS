#!/bin/bash

echo "🔍 فحص إعدادات DNS..."

DOMAIN="drs.smart-sense.site"

echo "🌐 فحص الدومين: $DOMAIN"

# فحص DNS
echo "📡 فحص DNS A record:"
nslookup $DOMAIN

echo ""
echo "📡 فحص DNS باستخدام dig:"
dig $DOMAIN A

echo ""
echo "🏓 اختبار ping:"
ping -c 4 $DOMAIN

echo ""
echo "🔌 فحص المنافذ:"
echo "المنفذ 80:"
nc -zv $DOMAIN 80 2>&1 || echo "المنفذ 80 مغلق أو غير متاح"

echo "المنفذ 443:"
nc -zv $DOMAIN 443 2>&1 || echo "المنفذ 443 مغلق أو غير متاح"

echo ""
echo "📋 ملاحظات:"
echo "1. تأكد من أن DNS يشير إلى IP الخادم"
echo "2. قد يستغرق انتشار DNS حتى 24 ساعة"
echo "3. استخدم https://whatsmydns.net للتحقق من انتشار DNS عالمياً"