#!/usr/bin/env python3
"""
سكربت التحقق من البيانات المستوردة
يقوم بفحص وعرض إحصائيات البيانات المستوردة من ملف Excel
"""

import sys
import os
from collections import defaultdict

# إضافة مسار المشروع للوصول للنماذج
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Region, Branch

class DataVerifier:
    def __init__(self):
        self.app = create_app()
    
    def get_statistics(self):
        """الحصول على إحصائيات البيانات"""
        with self.app.app_context():
            stats = {
                'total_users': User.query.count(),
                'total_regions': Region.query.count(),
                'total_branches': Branch.query.count(),
                'users_with_regions': 0,
                'users_with_branches': 0,
                'regions_by_user': defaultdict(int),
                'branches_by_user': defaultdict(int),
                'branches_by_governorate': defaultdict(int),
                'users_without_regions': [],
                'users_without_branches': [],
                'recent_users': []
            }
            
            # إحصائيات المستخدمين
            users = User.query.all()
            for user in users:
                # عدد المناطق والفروع لكل مستخدم
                region_count = len(user.assigned_regions)
                branch_count = len(user.assigned_branches)
                
                stats['regions_by_user'][user.employee_name] = region_count
                stats['branches_by_user'][user.employee_name] = branch_count
                
                if region_count > 0:
                    stats['users_with_regions'] += 1
                else:
                    stats['users_without_regions'].append(user.employee_name)
                
                if branch_count > 0:
                    stats['users_with_branches'] += 1
                else:
                    stats['users_without_branches'].append(user.employee_name)
            
            # إحصائيات الفروع حسب المحافظة
            branches = Branch.query.all()
            for branch in branches:
                if branch.governorate:
                    stats['branches_by_governorate'][branch.governorate] += 1
            
            # أحدث المستخدمين المضافين
            recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
            stats['recent_users'] = [
                {
                    'name': user.employee_name,
                    'username': user.username,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'regions_count': len(user.assigned_regions),
                    'branches_count': len(user.assigned_branches)
                }
                for user in recent_users
            ]
            
            return stats
    
    def print_statistics(self, stats):
        """طباعة الإحصائيات"""
        print("="*60)
        print("إحصائيات البيانات المستوردة")
        print("="*60)
        
        print(f"\n📊 الإحصائيات العامة:")
        print(f"   إجمالي المستخدمين: {stats['total_users']}")
        print(f"   إجمالي المناطق: {stats['total_regions']}")
        print(f"   إجمالي الفروع: {stats['total_branches']}")
        print(f"   المستخدمون الذين لديهم مناطق: {stats['users_with_regions']}")
        print(f"   المستخدمون الذين لديهم فروع: {stats['users_with_branches']}")
        
        print(f"\n🏢 أكثر المستخدمين نشاطاً (حسب عدد الفروع):")
        sorted_users = sorted(stats['branches_by_user'].items(), 
                            key=lambda x: x[1], reverse=True)[:10]
        for i, (user, count) in enumerate(sorted_users, 1):
            print(f"   {i:2d}. {user}: {count} فرع")
        
        print(f"\n🗺️ أكثر المحافظات (حسب عدد الفروع):")
        sorted_governorates = sorted(stats['branches_by_governorate'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
        for i, (gov, count) in enumerate(sorted_governorates, 1):
            print(f"   {i:2d}. {gov}: {count} فرع")
        
        print(f"\n👥 أحدث المستخدمين المضافين:")
        for i, user in enumerate(stats['recent_users'], 1):
            print(f"   {i:2d}. {user['name']} ({user['username']})")
            print(f"       تاريخ الإضافة: {user['created_at']}")
            print(f"       المناطق: {user['regions_count']}, الفروع: {user['branches_count']}")
        
        if stats['users_without_regions']:
            print(f"\n⚠️ مستخدمون بدون مناطق ({len(stats['users_without_regions'])}):")
            for user in stats['users_without_regions'][:5]:
                print(f"   - {user}")
            if len(stats['users_without_regions']) > 5:
                print(f"   ... و {len(stats['users_without_regions']) - 5} آخرين")
        
        if stats['users_without_branches']:
            print(f"\n⚠️ مستخدمون بدون فروع ({len(stats['users_without_branches'])}):")
            for user in stats['users_without_branches'][:5]:
                print(f"   - {user}")
            if len(stats['users_without_branches']) > 5:
                print(f"   ... و {len(stats['users_without_branches']) - 5} آخرين")
    
    def get_user_details(self, username_or_name):
        """الحصول على تفاصيل مستخدم محدد"""
        with self.app.app_context():
            # البحث بالاسم أو اسم المستخدم
            user = User.query.filter(
                (User.username == username_or_name) | 
                (User.employee_name == username_or_name)
            ).first()
            
            if not user:
                return None
            
            details = {
                'user_info': {
                    'name': user.employee_name,
                    'username': user.username,
                    'employee_code': user.employee_code,
                    'is_admin': user.is_admin,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                'regions': [],
                'branches': []
            }
            
            # المناطق
            for region in user.assigned_regions:
                region_info = {
                    'name': region.name,
                    'code': region.code,
                    'created_at': region.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'branches_count': len(region.branches)
                }
                details['regions'].append(region_info)
            
            # الفروع
            for branch in user.assigned_branches:
                branch_info = {
                    'name': branch.name,
                    'code': branch.code,
                    'governorate': branch.governorate,
                    'region': branch.region.name if branch.region else 'غير محدد',
                    'created_at': branch.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                details['branches'].append(branch_info)
            
            return details
    
    def print_user_details(self, details):
        """طباعة تفاصيل المستخدم"""
        if not details:
            print("❌ لم يتم العثور على المستخدم")
            return
        
        user = details['user_info']
        print("="*60)
        print(f"تفاصيل المستخدم: {user['name']}")
        print("="*60)
        
        print(f"\n👤 معلومات المستخدم:")
        print(f"   الاسم: {user['name']}")
        print(f"   اسم المستخدم: {user['username']}")
        print(f"   كود الموظف: {user['employee_code']}")
        print(f"   مدير: {'نعم' if user['is_admin'] else 'لا'}")
        print(f"   تاريخ الإنشاء: {user['created_at']}")
        
        print(f"\n🗺️ المناطق ({len(details['regions'])}):")
        for i, region in enumerate(details['regions'], 1):
            print(f"   {i:2d}. {region['name']}")
            print(f"       الكود: {region['code'] or 'غير محدد'}")
            print(f"       عدد الفروع: {region['branches_count']}")
            print(f"       تاريخ الإنشاء: {region['created_at']}")
        
        print(f"\n🏢 الفروع ({len(details['branches'])}):")
        for i, branch in enumerate(details['branches'], 1):
            print(f"   {i:2d}. {branch['name']} ({branch['code']})")
            print(f"       المحافظة: {branch['governorate'] or 'غير محدد'}")
            print(f"       المنطقة: {branch['region']}")
            print(f"       تاريخ الإنشاء: {branch['created_at']}")
    
    def run(self, user_search=None):
        """تشغيل عملية التحقق"""
        try:
            if user_search:
                # عرض تفاصيل مستخدم محدد
                details = self.get_user_details(user_search)
                self.print_user_details(details)
            else:
                # عرض الإحصائيات العامة
                stats = self.get_statistics()
                self.print_statistics(stats)
            
            return True
        except Exception as e:
            print(f"❌ خطأ في التحقق من البيانات: {str(e)}")
            return False

def main():
    """الدالة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(description='التحقق من البيانات المستوردة')
    parser.add_argument('--user', '-u', help='البحث عن مستخدم محدد (بالاسم أو اسم المستخدم)')
    
    args = parser.parse_args()
    
    verifier = DataVerifier()
    return verifier.run(args.user)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)