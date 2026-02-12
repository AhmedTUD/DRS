#!/usr/bin/env python3
"""
سكربت استيراد المشرفين المحسن - إصدار متقدم
يتضمن ميزات إضافية مثل:
- تحديث البيانات الموجودة
- معالجة أفضل للأخطاء
- تقارير مفصلة
- إمكانية التشغيل الجاف (Dry Run)
"""

import pandas as pd
import sys
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash
import re
import argparse

# إضافة مسار المشروع للوصول للنماذج
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Region, Branch

class AdvancedSupervisorImporter:
    def __init__(self, excel_file_path, dry_run=False, update_existing=False):
        self.excel_file_path = excel_file_path
        self.dry_run = dry_run
        self.update_existing = update_existing
        self.app = create_app()
        self.stats = {
            'new_users': 0,
            'updated_users': 0,
            'new_regions': 0,
            'updated_regions': 0,
            'new_branches': 0,
            'updated_branches': 0,
            'existing_users': 0,
            'existing_regions': 0,
            'existing_branches': 0,
            'errors': [],
            'warnings': [],
            'processed_rows': 0,
            'skipped_rows': 0
        }
        self.detailed_log = []
    
    def log_action(self, action_type, message, details=None):
        """تسجيل العمليات بالتفصيل"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': action_type,
            'message': message,
            'details': details or {}
        }
        self.detailed_log.append(log_entry)
        
        if action_type == 'error':
            self.stats['errors'].append(message)
        elif action_type == 'warning':
            self.stats['warnings'].append(message)
    
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
            self.log_action('info', f"تم العثور على مستخدم موجود: {supervisor_name}")
            
            # تحديث البيانات إذا كان مطلوباً
            if self.update_existing:
                # يمكن إضافة منطق تحديث هنا إذا لزم الأمر
                self.stats['updated_users'] += 1
                self.log_action('update', f"تم تحديث بيانات المستخدم: {supervisor_name}")
            
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
        
        # كلمة مرور افتراضية
        default_password = "123456"
        
        user = User(
            employee_name=supervisor_name,
            employee_code=employee_code,
            username=username,
            password_hash=generate_password_hash(default_password),
            is_admin=False
        )
        
        try:
            if not self.dry_run:
                db.session.add(user)
                db.session.flush()
            
            self.stats['new_users'] += 1
            self.log_action('create', f"تم إنشاء مستخدم جديد: {supervisor_name}", {
                'username': username,
                'employee_code': employee_code
            })
            print(f"✓ تم إنشاء مستخدم جديد: {supervisor_name} (Username: {username})")
            return user
        except Exception as e:
            error_msg = f"خطأ في إنشاء المستخدم {supervisor_name}: {str(e)}"
            self.log_action('error', error_msg)
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
            self.log_action('info', f"تم العثور على منطقة موجودة: {region_name} للمشرف: {owner_user.employee_name}")
            return region
        
        # إنشاء منطقة جديدة
        region = Region(
            name=region_name,
            owner_user_id=owner_user.id
        )
        
        try:
            if not self.dry_run:
                db.session.add(region)
                db.session.flush()
            
            self.stats['new_regions'] += 1
            self.log_action('create', f"تم إنشاء منطقة جديدة: {region_name}", {
                'owner': owner_user.employee_name
            })
            print(f"  ✓ تم إنشاء منطقة جديدة: {region_name} للمشرف: {owner_user.employee_name}")
            return region
        except Exception as e:
            error_msg = f"خطأ في إنشاء المنطقة {region_name}: {str(e)}"
            self.log_action('error', error_msg)
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
            self.log_action('info', f"تم العثور على فرع موجود: {shop_name} ({shop_code})")
            
            # تحديث البيانات إذا كان مطلوباً
            if self.update_existing:
                updated = False
                if branch.name != shop_name:
                    branch.name = shop_name
                    updated = True
                if branch.governorate != self.clean_name(governorate):
                    branch.governorate = self.clean_name(governorate)
                    updated = True
                if region and branch.region_id != region.id:
                    branch.region_id = region.id
                    updated = True
                
                if updated and not self.dry_run:
                    self.stats['updated_branches'] += 1
                    self.log_action('update', f"تم تحديث بيانات الفرع: {shop_name}")
            
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
            if not self.dry_run:
                db.session.add(branch)
                db.session.flush()
            
            self.stats['new_branches'] += 1
            self.log_action('create', f"تم إنشاء فرع جديد: {shop_name}", {
                'code': shop_code,
                'governorate': governorate,
                'region': region.name if region else None
            })
            print(f"    ✓ تم إنشاء فرع جديد: {shop_name} ({shop_code})")
            return branch
        except Exception as e:
            error_msg = f"خطأ في إنشاء الفرع {shop_name}: {str(e)}"
            self.log_action('error', error_msg)
            return None
    
    def assign_relationships(self, user, region, branch):
        """ربط المستخدم بالمنطقة والفرع"""
        try:
            # ربط المستخدم بالمنطقة
            if region and region not in user.assigned_regions:
                if not self.dry_run:
                    user.assigned_regions.append(region)
                self.log_action('assign', f"تم ربط المستخدم {user.employee_name} بالمنطقة {region.name}")
            
            # ربط المستخدم بالفرع
            if branch and branch not in user.assigned_branches:
                if not self.dry_run:
                    user.assigned_branches.append(branch)
                self.log_action('assign', f"تم ربط المستخدم {user.employee_name} بالفرع {branch.name}")
                
        except Exception as e:
            error_msg = f"خطأ في ربط العلاقات: {str(e)}"
            self.log_action('error', error_msg)
    
    def detect_supervisor_columns(self, df):
        """اكتشاف كل الأعمدة التي تحتوي على كلمة supervisor أو SPVR"""
        supervisor_cols = []
        
        for col in df.columns:
            col_str = str(col).upper()
            # البحث عن أي عمود يحتوي على SPVR أو SUPERVISOR
            if 'SPVR' in col_str or 'SUPERVISOR' in col_str:
                supervisor_cols.append(col)
        
        return supervisor_cols
    
    def validate_row_data(self, row, supervisor_columns):
        """التحقق من صحة بيانات الصف"""
        warnings = []
        
        shop_code = self.clean_name(row.get('Shop Code'))
        shop_name = self.clean_name(row.get('Shop Name'))
        area_name = self.clean_name(row.get('Area'))
        
        if not shop_code:
            warnings.append("كود المتجر مفقود")
        if not shop_name:
            warnings.append("اسم المتجر مفقود")
        if not area_name:
            warnings.append("اسم المنطقة مفقود")
        
        # التحقق من وجود مشرف واحد على الأقل
        has_supervisor = any(self.clean_name(row.get(col)) for col in supervisor_columns)
        
        if not has_supervisor:
            warnings.append("لا يوجد مشرف محدد")
        
        return warnings
    
    def process_excel_file(self):
        """معالجة ملف Excel الرئيسية"""
        try:
            print(f"قراءة ملف Excel: {self.excel_file_path}")
            if self.dry_run:
                print("🔍 وضع التشغيل الجاف - لن يتم حفظ أي تغييرات")
            
            df = pd.read_excel(self.excel_file_path)
            print(f"تم العثور على {len(df)} صف")
            
            # اكتشاف أعمدة المشرفين تلقائياً
            supervisor_columns = self.detect_supervisor_columns(df)
            
            if not supervisor_columns:
                print("⚠️ لم يتم العثور على أي أعمدة للمشرفين!")
                print("تأكد من وجود أعمدة تحتوي على 'SPVR' أو 'Supervisor' في الملف")
                return
            
            print(f"\n✅ تم اكتشاف {len(supervisor_columns)} عمود للمشرفين:")
            for i, col in enumerate(supervisor_columns, 1):
                print(f"  {i}. {col}")
            print()
            
            # معالجة كل صف
            for index, row in df.iterrows():
                try:
                    self.stats['processed_rows'] += 1
                    
                    # التحقق من صحة البيانات
                    warnings = self.validate_row_data(row, supervisor_columns)
                    if warnings:
                        for warning in warnings:
                            self.log_action('warning', f"الصف {index + 1}: {warning}")
                        
                        # تخطي الصف إذا كانت البيانات الأساسية مفقودة
                        if "كود المتجر مفقود" in warnings or "اسم المتجر مفقود" in warnings:
                            self.stats['skipped_rows'] += 1
                            continue
                    
                    shop_code = self.clean_name(row.get('Shop Code'))
                    shop_name = self.clean_name(row.get('Shop Name'))
                    area_name = self.clean_name(row.get('Area'))
                    governorate = self.clean_name(row.get('Governorate'))
                    
                    # معالجة كل مشرف في الصف
                    for col in supervisor_columns:
                        supervisor_name = self.clean_name(row.get(col))
                        
                        if not supervisor_name:
                            continue
                        
                        print(f"\nمعالجة المشرف: {supervisor_name} (من عمود: {col})")
                        
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
                    self.log_action('error', error_msg)
                    print(f"⚠️ {error_msg}")
                    continue
            
            # حفظ التغييرات
            if not self.dry_run:
                db.session.commit()
                print("\n✅ تم حفظ جميع التغييرات بنجاح")
            else:
                print("\n🔍 انتهى التشغيل الجاف - لم يتم حفظ أي تغييرات")
            
        except Exception as e:
            if not self.dry_run:
                db.session.rollback()
            error_msg = f"خطأ عام في معالجة الملف: {str(e)}"
            self.log_action('error', error_msg)
            print(f"❌ {error_msg}")
            raise
    
    def generate_report(self):
        """إنشاء تقرير مفصل"""
        report = {
            'summary': self.stats,
            'detailed_log': self.detailed_log,
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'update_existing': self.update_existing
        }
        
        # حفظ التقرير في ملف JSON
        report_filename = f"import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 تم حفظ التقرير المفصل في: {report_filename}")
        return report_filename
    
    def print_statistics(self):
        """طباعة إحصائيات العملية"""
        print("\n" + "="*50)
        print("إحصائيات عملية الاستيراد:")
        print("="*50)
        print(f"الصفوف المعالجة: {self.stats['processed_rows']}")
        print(f"الصفوف المتخطاة: {self.stats['skipped_rows']}")
        print(f"المستخدمون الجدد: {self.stats['new_users']}")
        print(f"المستخدمون المحدثون: {self.stats['updated_users']}")
        print(f"المستخدمون الموجودون: {self.stats['existing_users']}")
        print(f"المناطق الجديدة: {self.stats['new_regions']}")
        print(f"المناطق المحدثة: {self.stats['updated_regions']}")
        print(f"المناطق الموجودة: {self.stats['existing_regions']}")
        print(f"الفروع الجديدة: {self.stats['new_branches']}")
        print(f"الفروع المحدثة: {self.stats['updated_branches']}")
        print(f"الفروع الموجودة: {self.stats['existing_branches']}")
        
        if self.stats['warnings']:
            print(f"\nالتحذيرات ({len(self.stats['warnings'])}):")
            for warning in self.stats['warnings'][:5]:  # عرض أول 5 تحذيرات فقط
                print(f"  ⚠️ {warning}")
            if len(self.stats['warnings']) > 5:
                print(f"  ... و {len(self.stats['warnings']) - 5} تحذير آخر")
        
        if self.stats['errors']:
            print(f"\nالأخطاء ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # عرض أول 5 أخطاء فقط
                print(f"  ❌ {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... و {len(self.stats['errors']) - 5} خطأ آخر")
    
    def run(self):
        """تشغيل عملية الاستيراد"""
        with self.app.app_context():
            try:
                print("بدء عملية استيراد المشرفين المحسنة...")
                self.process_excel_file()
                self.print_statistics()
                report_file = self.generate_report()
                
                if self.dry_run:
                    print("\n🔍 انتهى التشغيل الجاف بنجاح!")
                else:
                    print("\n✅ تمت عملية الاستيراد بنجاح!")
                
                return True
            except Exception as e:
                print(f"\n❌ فشلت عملية الاستيراد: {str(e)}")
                return False

def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description='استيراد المشرفين من ملف Excel - الإصدار المحسن')
    parser.add_argument('--file', '-f', default="Shop_List_2025-M08 (2).xlsx", 
                       help='مسار ملف Excel')
    parser.add_argument('--dry-run', '-d', action='store_true', 
                       help='تشغيل جاف - عرض النتائج بدون حفظ')
    parser.add_argument('--update', '-u', action='store_true', 
                       help='تحديث البيانات الموجودة')
    
    args = parser.parse_args()
    
    # التحقق من وجود الملف
    if not os.path.exists(args.file):
        print(f"❌ لم يتم العثور على الملف: {args.file}")
        print("تأكد من وجود الملف في المسار المحدد")
        return False
    
    # تشغيل عملية الاستيراد
    importer = AdvancedSupervisorImporter(
        excel_file_path=args.file,
        dry_run=args.dry_run,
        update_existing=args.update
    )
    return importer.run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
