#!/usr/bin/env python3
"""
إنشاء المستخدمين يدوياً مع التأكد من جميع الحقول المطلوبة
"""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_users_manual():
    """إنشاء المستخدمين يدوياً"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # حذف المستخدمين الموجودين
            print("🧹 حذف المستخدمين الموجودين...")
            User.query.delete()
            db.session.commit()
            
            # إنشاء المدير
            print("👨‍💼 إنشاء المدير...")
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
            print("👨‍💻 إنشاء الموظف...")
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
            
            print("✅ تم إنشاء المستخدمين بنجاح!")
            
            # التحقق من المستخدمين
            users = User.query.all()
            print(f"\n📊 عدد المستخدمين: {len(users)}")
            for user in users:
                print(f"   - {user.username}: {user.employee_name} ({'مدير' if user.is_admin else 'موظف'})")
            
            print("\n🔐 بيانات تسجيل الدخول:")
            print("   المدير: admin / admin123")
            print("   الموظف: employee / employee123")
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء المستخدمين: {e}")
            db.session.rollback()
            
            # طباعة تفاصيل الخطأ
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 إنشاء المستخدمين يدوياً...")
    print("=" * 50)
    create_users_manual()