#!/bin/bash

echo "👥 إنشاء المستخدمين التجريبيين (محدث)..."

# حذف المستخدمين الموجودين إذا كانوا موجودين
echo "🧹 حذف المستخدمين القدامى..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    try:
        User.query.filter_by(username='admin').delete()
        User.query.filter_by(username='employee').delete()
        db.session.commit()
        print('تم حذف المستخدمين القدامى')
    except:
        pass
"

# إنشاء المستخدمين الجدد
echo "✨ إنشاء المستخدمين الجدد..."
docker-compose -f docker-compose.simple.yml exec web python create_demo_users.py

echo "✅ تم إنشاء المستخدمين بنجاح!"
echo ""
echo "🔐 بيانات تسجيل الدخول:"
echo "المدير: admin / admin123"
echo "الموظف: employee / employee123"