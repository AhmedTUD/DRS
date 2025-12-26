#!/usr/bin/env python3
"""
Create demo users for Daily Report System
Run this after deploying to PythonAnywhere
"""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_demo_users():
    """Create demo admin and employee users"""
    
    app = create_app()
    
    with app.app_context():
        # Check if users already exist
        if User.query.filter_by(username='admin').first():
            print("⚠️  Users already exist!")
            return
        
        try:
            # Create admin user
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                employee_name='مدير النظام',
                employee_code='ADMIN001',
                is_admin=True
            )
            db.session.add(admin)
            print("✅ Created admin user: admin/admin123")
            
            # Create employee user
            employee = User(
                username='employee',
                password_hash=generate_password_hash('employee123'),
                employee_name='موظف تجريبي',
                employee_code='EMP001',
                is_admin=False
            )
            db.session.add(employee)
            print("✅ Created employee user: employee/employee123")
            
            # Commit changes
            db.session.commit()
            print("\n🎉 Demo users created successfully!")
            print("\n📋 Login credentials:")
            print("   Admin: admin / admin123")
            print("   Employee: employee / employee123")
            
        except Exception as e:
            print(f"❌ Error creating users: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🚀 Creating demo users for Daily Report System...")
    print("=" * 50)
    create_demo_users()