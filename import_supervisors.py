#!/usr/bin/env python3
"""
سكربت استيراد المشرفين من ملف Excel
يقوم بإنشاء المستخدمين والمناطق والفروع بناءً على بيانات Excel
مع تجنب التكرار والحفاظ على البيانات الموجودة
"""

import pandas as pd
import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
import re

# إضافة مسار المشروع للوصول للنماذج
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Region, Branch

class SupervisorImporter:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.app = create_app()
        self.stats = {
            'new_users': 0,
            'new_regions': 0,
            'new_branches': 0,
            'existing_users': 0,
            'existing_regions': 0,
            'existing_branches': 0,
            'errors': []
        }
    
    def clean_name(self, name):
        """تنظيف الأسماء من المسافات الزائدة والقيم الفارغة"""
        if pd.isna(name) or name is None:
            return None
        name = str(name).strip()
        return name if name and name.lower() != 'nan' else None
    
    def generate_username(self, name):
        """إنشاء اسم مستخدم من الاسم"""
        if not name:
            return None
        
        # إزالة المسافات والرموز الخاصة
        username = re.sub(r'[^\w\s]', '', name)
        username = re.sub(r'\s+', '_', username.strip())
        username = username.lower()
        
        # التأكد من عدم تجاوز 80 حرف
        if len(username) > 80:
            username = username[:80]
        
        return username
    
    def generate_employee_code(self, name):
        """إنشاء كود موظف من الاسم"""
        if not name:
            return None
        
        # أخذ الأحرف الأولى من كل كلمة + رقم عشوائي
        words = name.split()
        code = ''.join([word[0].upper() for word in words if word])
        
        # إضافة timestamp للتأكد من التفرد
        timestamp = str(int(datetime.now().timestamp()))[-4:]
        code = f"SUP_{code}_{timestamp}"
        
        return code[:50]  # التأكد من عدم تجاوز 50 حرف
    
    def get_or_create_user(self, supervisor_name):
        """الحصول على المستخدم أو إنشاؤه إذا لم يكن موجوداً"""
        if not supervisor_name:
            return None
        
        # البحث عن المستخدم بالاسم أولاً
        user = User.query.filter_by(employee_name=supervisor_name).first()
        
        if user:
            self.stats['existing_users'] += 1
            return user
        
        # إنشاء مستخدم جديد
        username = self.generate_username(supervisor_name)
        employee_code = self.generate_employee_code(supervisor_name)
        
        # التأكد من عدم تكرار اسم المستخدم
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}_{counter}"
            counter += 1
        
        # التأكد من عدم تكرار كود الموظف
        counter = 1
        original_code = employee_code
        while User.query.filter_by(employee_code=employee_code).first():
            employee_code = f"{original_code}_{counter}"
            counter += 1
        
        # كلمة مرور افتراضية (يجب تغييرها عند أول تسجيل دخول)
        default_password = "123456"
        
        user = User(
            employee_name=supervisor_name,
            employee_code=employee_code,
            username=username,
            password_hash=generate_password_hash(default_password),
            is_admin=False
        )
        
        try:
            db.session.add(user)
            db.session.flush()  # للحصول على ID بدون commit
            self.stats['new_users'] += 1
            print(f"✓ تم إنشاء مستخدم جديد: {supervisor_name} (Username: {username})")
            return user
        except Exception as e:
            self.stats['errors'].append(f"خطأ في إنشاء المستخدم {supervisor_name}: {str(e)}")
            return None
    
    def get_or_create_region(self, region_name, owner_user):
        """الحصول على المنطقة أو إنشاؤها إذا لم تكن موجودة"""
        if not region_name or not owner_user:
            return None
        
        # البحث عن المنطقة للمستخدم المحدد
        region = Region.query.filter_by(
            name=region_name, 
            owner_user_id=owner_user.id
        ).first()
        
        if region:
            self.stats['existing_regions'] += 1
            return region
        
        # إنشاء منطقة جديدة
        region = Region(
            name=region_name,
            owner_user_id=owner_user.id
        )
        
        try:
            db.session.add(region)
            db.session.flush()
            self.stats['new_regions'] += 1
            print(f"  ✓ تم إنشاء منطقة جديدة: {region_name} للمشرف: {owner_user.employee_name}")
            return region
        except Exception as e:
            self.stats['errors'].append(f"خطأ في إنشاء المنطقة {region_name}: {str(e)}")
            return None
    
    def get_or_create_branch(self, shop_code, shop_name, region, governorate, owner_user):
        """الحصول على الفرع أو إنشاؤه إذا لم يكن موجوداً"""
        if not shop_code or not shop_name or not owner_user:
            return None
        
        # البحث عن الفرع للمستخدم المحدد
        branch = Branch.query.filter_by(
            code=shop_code,
            owner_user_id=owner_user.id
        ).first()
        
        if branch:
            self.stats['existing_branches'] += 1
            return branch
        
        # إنشاء فرع جديد
        branch = Branch(
            name=shop_name,
            code=shop_code,
            region_id=region.id if region else None,
            governorate=self.clean_name(governorate),
            owner_user_id=owner_user.id
        )
        
        try:
            db.session.add(branch)
            db.session.flush()
            self.stats['new_branches'] += 1
            print(f"    ✓ تم إنشاء فرع جديد: {shop_name} ({shop_code})")
            return branch
        except Exception as e:
            self.stats['errors'].append(f"خطأ في إنشاء الفرع {shop_name}: {str(e)}")
            return None
    
    def assign_relationships(self, user, region, branch):
        """ربط المستخدم بالمنطقة والفرع"""
        try:
            # ربط المستخدم بالمنطقة
            if region and region not in user.assigned_regions:
                user.assigned_regions.append(region)
            
            # ربط المستخدم بالفرع
            if branch and branch not in user.assigned_branches:
                user.assigned_branches.append(branch)
                
        except Exception as e:
            self.stats['errors'].append(f"خطأ في ربط العلاقات: {str(e)}")
    
    def process_excel_file(self):
        """معالجة ملف Excel الرئيسية"""
        try:
            print(f"قراءة ملف Excel: {self.excel_file_path}")
            df = pd.read_excel(self.excel_file_path)
            
            print(f"تم العثور على {len(df)} صف")
            
            # تحديد أعمدة المشرفين (SPVR, SPVR.1, SPVR.2)
            supervisor_columns = ['SPVR', 'SPVR.1', 'SPVR.2']
            
            # معالجة كل صف
            for index, row in df.iterrows():
                try:
                    shop_code = self.clean_name(row.get('Shop Code'))
                    shop_name = self.clean_name(row.get('Shop Name'))
                    area_name = self.clean_name(row.get('Area'))
                    governorate = self.clean_name(row.get('Governorate'))
                    
                    if not shop_code or not shop_name:
                        continue
                    
                    # معالجة كل مشرف في الصف
                    for col in supervisor_columns:
                        supervisor_name = self.clean_name(row.get(col))
                        
                        if not supervisor_name:
                            continue
                        
                        print(f"\nمعالجة المشرف: {supervisor_name}")
                        
                        # إنشاء أو الحصول على المستخدم
                        user = self.get_or_create_user(supervisor_name)
                        if not user:
                            continue
                        
                        # إنشاء أو الحصول على المنطقة
                        region = None
                        if area_name:
                            region = self.get_or_create_region(area_name, user)
                        
                        # إنشاء أو الحصول على الفرع
                        branch = self.get_or_create_branch(
                            shop_code, shop_name, region, governorate, user
                        )
                        
                        # ربط العلاقات
                        self.assign_relationships(user, region, branch)
                
                except Exception as e:
                    error_msg = f"خطأ في معالجة الصف {index + 1}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"⚠️ {error_msg}")
                    continue
            
            # حفظ التغييرات
            db.session.commit()
            print("\n✅ تم حفظ جميع التغييرات بنجاح")
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"خطأ عام في معالجة الملف: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    def print_statistics(self):
        """طباعة إحصائيات العملية"""
        print("\n" + "="*50)
        print("إحصائيات عملية الاستيراد:")
        print("="*50)
        print(f"المستخدمون الجدد: {self.stats['new_users']}")
        print(f"المستخدمون الموجودون: {self.stats['existing_users']}")
        print(f"المناطق الجديدة: {self.stats['new_regions']}")
        print(f"المناطق الموجودة: {self.stats['existing_regions']}")
        print(f"الفروع الجديدة: {self.stats['new_branches']}")
        print(f"الفروع الموجودة: {self.stats['existing_branches']}")
        
        if self.stats['errors']:
            print(f"\nالأخطاء ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:  # عرض أول 10 أخطاء فقط
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... و {len(self.stats['errors']) - 10} خطأ آخر")
    
    def run(self):
        """تشغيل عملية الاستيراد"""
        with self.app.app_context():
            try:
                print("بدء عملية استيراد المشرفين...")
                self.process_excel_file()
                self.print_statistics()
                print("\n✅ تمت عملية الاستيراد بنجاح!")
                return True
            except Exception as e:
                print(f"\n❌ فشلت عملية الاستيراد: {str(e)}")
                return False

def main():
    """الدالة الرئيسية"""
    excel_file = "Shop_List_2025-M08 (2).xlsx"
    
    # التحقق من وجود الملف
    if not os.path.exists(excel_file):
        print(f"❌ لم يتم العثور على الملف: {excel_file}")
        print("تأكد من وجود الملف في نفس مجلد السكربت")
        return False
    
    # تشغيل عملية الاستيراد
    importer = SupervisorImporter(excel_file)
    return importer.run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)