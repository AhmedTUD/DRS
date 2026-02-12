#!/usr/bin/env python3
"""
سكريبت إضافة فروع لمستخدمين موجودين
يقوم بإضافة فروع جديدة أو ربط فروع موجودة بمستخدمين محددين
"""

import pandas as pd
import sys
import os
from datetime import datetime

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Region, Branch

class BranchAdder:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.app = create_app()
        self.stats = {
            'users_found': 0,
            'users_not_found': 0,
            'new_branches': 0,
            'existing_branches': 0,
            'new_regions': 0,
            'existing_regions': 0,
            'branches_assigned': 0,
            'errors': [],
            'warnings': []
        }
    
    def clean_name(self, name):
        """تنظيف الأسماء من المسافات الزائدة"""
        if pd.isna(name) or name is None:
            return None
        name = str(name).strip()
        return name if name and name.lower() != 'nan' else None
    
    def find_user(self, identifier):
        """البحث عن المستخدم بالاسم أو اسم المستخدم أو كود الموظف"""
        if not identifier:
            return None
        
        identifier = self.clean_name(identifier)
        
        # البحث بالاسم
        user = User.query.filter_by(employee_name=identifier).first()
        if user:
            return user
        
        # البحث باسم المستخدم
        user = User.query.filter_by(username=identifier).first()
        if user:
            return user
        
        # البحث بكود الموظف
        user = User.query.filter_by(employee_code=identifier).first()
        if user:
            return user
        
        return None
    
    def get_or_create_region(self, region_name, owner_user):
        """الحصول على المنطقة أو إنشاؤها"""
        if not region_name or not owner_user:
            return None
        
        # البحث عن المنطقة
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
            print(f"  ✓ تم إنشاء منطقة جديدة: {region_name}")
            return region
        except Exception as e:
            self.stats['errors'].append(f"خطأ في إنشاء المنطقة {region_name}: {str(e)}")
            return None
    
    def get_or_create_branch(self, branch_code, branch_name, region, governorate, owner_user):
        """الحصول على الفرع أو إنشاؤه"""
        if not branch_code or not branch_name or not owner_user:
            return None
        
        # البحث عن الفرع
        branch = Branch.query.filter_by(
            code=branch_code,
            owner_user_id=owner_user.id
        ).first()
        
        if branch:
            self.stats['existing_branches'] += 1
            print(f"    ℹ️ الفرع موجود: {branch_name} ({branch_code})")
            return branch
        
        # إنشاء فرع جديد
        branch = Branch(
            name=branch_name,
            code=branch_code,
            region_id=region.id if region else None,
            governorate=self.clean_name(governorate),
            owner_user_id=owner_user.id
        )
        
        try:
            db.session.add(branch)
            db.session.flush()
            self.stats['new_branches'] += 1
            print(f"    ✓ تم إنشاء فرع جديد: {branch_name} ({branch_code})")
            return branch
        except Exception as e:
            self.stats['errors'].append(f"خطأ في إنشاء الفرع {branch_name}: {str(e)}")
            return None
    
    def assign_branch_to_user(self, user, branch):
        """ربط الفرع بالمستخدم"""
        if not user or not branch:
            return False
        
        try:
            if branch not in user.assigned_branches:
                user.assigned_branches.append(branch)
                self.stats['branches_assigned'] += 1
                print(f"      ✓ تم ربط الفرع بالمستخدم")
                return True
            else:
                print(f"      ℹ️ الفرع مربوط بالفعل بالمستخدم")
                return False
        except Exception as e:
            self.stats['errors'].append(f"خطأ في ربط الفرع: {str(e)}")
            return False
    
    def assign_region_to_user(self, user, region):
        """ربط المنطقة بالمستخدم"""
        if not user or not region:
            return False
        
        try:
            if region not in user.assigned_regions:
                user.assigned_regions.append(region)
                return True
            return False
        except Exception as e:
            self.stats['errors'].append(f"خطأ في ربط المنطقة: {str(e)}")
            return False
    
    def process_excel_file(self):
        """معالجة ملف Excel"""
        try:
            print(f"📖 قراءة ملف Excel: {self.excel_file_path}\n")
            df = pd.read_excel(self.excel_file_path)
            
            print(f"تم العثور على {len(df)} صف\n")
            
            # البحث عن جميع أعمدة المشرفين تلقائياً
            # يبحث عن أي عمود يبدأ بـ "SPVR" أو يساوي "SPVR"
            supervisor_columns = [col for col in df.columns if col == 'SPVR' or (isinstance(col, str) and col.startswith('SPVR.'))]
            
            if not supervisor_columns:
                print("❌ لم يتم العثور على أعمدة المشرفين (SPVR)")
                return
            
            print(f"✓ تم العثور على {len(supervisor_columns)} عمود للمشرفين:")
            for col in supervisor_columns:
                print(f"  • {col}")
            print("\n" + "="*60)
            
            # معالجة كل صف
            for index, row in df.iterrows():
                try:
                    # قراءة بيانات الفرع
                    branch_code = self.clean_name(row.get('Shop Code'))
                    branch_name = self.clean_name(row.get('Shop Name'))
                    region_name = self.clean_name(row.get('Area'))
                    governorate = self.clean_name(row.get('Governorate'))
                    
                    # التحقق من البيانات الأساسية
                    if not branch_code or not branch_name:
                        self.stats['warnings'].append(f"الصف {index + 2}: بيانات الفرع مفقودة")
                        continue
                    
                    # معالجة كل مشرف في الصف
                    for col in supervisor_columns:
                        user_identifier = self.clean_name(row.get(col))
                        
                        if not user_identifier:
                            continue
                        
                        print(f"\n[الصف {index + 2}] معالجة: {user_identifier} - {branch_name}")
                        
                        # البحث عن المستخدم
                        user = self.find_user(user_identifier)
                        
                        if not user:
                            self.stats['users_not_found'] += 1
                            error_msg = f"الصف {index + 2}: المستخدم غير موجود: {user_identifier}"
                            self.stats['errors'].append(error_msg)
                            print(f"  ❌ {error_msg}")
                            continue
                        
                        self.stats['users_found'] += 1
                        print(f"  ✓ تم العثور على المستخدم: {user.employee_name}")
                        
                        # إنشاء أو الحصول على المنطقة
                        region = None
                        if region_name:
                            region = self.get_or_create_region(region_name, user)
                            if region:
                                self.assign_region_to_user(user, region)
                        
                        # إنشاء أو الحصول على الفرع
                        branch = self.get_or_create_branch(
                            branch_code, branch_name, region, governorate, user
                        )
                        
                        # ربط الفرع بالمستخدم
                        if branch:
                            self.assign_branch_to_user(user, branch)
                    
                except Exception as e:
                    error_msg = f"خطأ في معالجة الصف {index + 2}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"  ⚠️ {error_msg}")
                    continue
            
            # حفظ التغييرات
            db.session.commit()
            print("\n" + "="*60)
            print("✅ تم حفظ جميع التغييرات بنجاح")
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"خطأ عام في معالجة الملف: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    def print_statistics(self):
        """طباعة إحصائيات العملية"""
        print("\n" + "="*60)
        print("📊 إحصائيات عملية إضافة الفروع:")
        print("="*60)
        print(f"✓ المستخدمون الموجودون: {self.stats['users_found']}")
        print(f"✗ المستخدمون غير الموجودين: {self.stats['users_not_found']}")
        print(f"➕ المناطق الجديدة: {self.stats['new_regions']}")
        print(f"ℹ️ المناطق الموجودة: {self.stats['existing_regions']}")
        print(f"➕ الفروع الجديدة: {self.stats['new_branches']}")
        print(f"ℹ️ الفروع الموجودة: {self.stats['existing_branches']}")
        print(f"🔗 عمليات الربط: {self.stats['branches_assigned']}")
        
        if self.stats['warnings']:
            print(f"\n⚠️ التحذيرات ({len(self.stats['warnings'])}):")
            for warning in self.stats['warnings'][:5]:
                print(f"  • {warning}")
            if len(self.stats['warnings']) > 5:
                print(f"  ... و {len(self.stats['warnings']) - 5} تحذير آخر")
        
        if self.stats['errors']:
            print(f"\n❌ الأخطاء ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:
                print(f"  • {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... و {len(self.stats['errors']) - 5} خطأ آخر")
    
    def run(self):
        """تشغيل عملية إضافة الفروع"""
        with self.app.app_context():
            try:
                print("\n🚀 بدء عملية إضافة الفروع للمستخدمين...\n")
                self.process_excel_file()
                self.print_statistics()
                print("\n✅ تمت العملية بنجاح!\n")
                return True
            except Exception as e:
                print(f"\n❌ فشلت العملية: {str(e)}\n")
                return False

def main():
    """الدالة الرئيسية"""
    # اسم ملف Excel الافتراضي (نفس ملف الاستيراد الأصلي)
    excel_file = "Shop_List_2025-M08 (2).xlsx"
    
    # التحقق من وجود الملف
    if not os.path.exists(excel_file):
        print(f"❌ لم يتم العثور على الملف: {excel_file}")
        print("\nيرجى التأكد من وجود ملف Excel يحتوي على:")
        print("  - Shop Code: كود الفرع")
        print("  - Shop Name: اسم الفرع")
        print("  - Area: اسم المنطقة")
        print("  - Governorate: اسم المحافظة")
        print("  - SPVR, SPVR.1, SPVR.2: أسماء المشرفين")
        return False
    
    # تشغيل عملية إضافة الفروع
    adder = BranchAdder(excel_file)
    return adder.run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
