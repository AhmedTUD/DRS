#!/bin/bash

echo "👥 إنشاء المستخدمين مباشرة..."

# إنشاء المستخدمين مباشرة بدون ملف منفصل
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

print('🚀 إنشاء المستخدمين...')

app = create_app()
with app.app_context():
    try:
        # حذف المستخدمين الموجودين
        print('🧹 حذف المستخدمين الموجودين...')
        User.query.delete()
        db.session.commit()
        
        # إنشاء المدير
        print('👨‍💼 إنشاء المدير...')
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            employee_name='مدير النظام',
            employee_code='ADMIN001',
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        
        # إنشاء الموظف
        print('👨‍💻 إنشاء الموظف...')
        employee = User(
            username='employee',
            password_hash=generate_password_hash('employee123'),
            employee_name='موظف تجريبي',
            employee_code='EMP001',
            is_admin=False,
            created_at=datetime.utcnow()
        )
        db.session.add(employee)
        
        # حفظ التغييرات
        db.session.commit()
        
        print('✅ تم إنشاء المستخدمين بنجاح!')
        
        # التحقق من المستخدمين
        users = User.query.all()
        print(f'📊 عدد المستخدمين: {len(users)}')
        for user in users:
            print(f'   - {user.username}: {user.employee_name} ({\"مدير\" if user.is_admin else \"موظف\"})')
        
    except Exception as e:
        print(f'❌ خطأ في إنشاء المستخدمين: {e}')
        db.session.rollback()
        import traceback
        traceback.print_exc()
"

# اختبار تسجيل الدخول
echo ""
echo "🧪 اختبار تسجيل الدخول..."
docker-compose -f docker-compose.simple.yml exec web python -c "
from app import create_app
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    # اختبار المدير
    admin = User.query.filter_by(username='admin').first()
    if admin:
        if check_password_hash(admin.password_hash, 'admin123'):
            print('✅ تسجيل دخول المدير يعمل: admin / admin123')
        else:
            print('❌ كلمة مرور المدير خاطئة')
    else:
        print('❌ المدير غير موجود')
    
    # اختبار الموظف
    employee = User.query.filter_by(username='employee').first()
    if employee:
        if check_password_hash(employee.password_hash, 'employee123'):
            print('✅ تسجيل دخول الموظف يعمل: employee / employee123')
        else:
            print('❌ كلمة مرور الموظف خاطئة')
    else:
        print('❌ الموظف غير موجود')
"

echo ""
echo "🎉 تم الانتهاء!"
echo "🔐 بيانات تسجيل الدخول:"
echo "المدير: admin / admin123"
echo "الموظف: employee / employee123"