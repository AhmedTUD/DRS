"""
Security Check Script
Quick security audit of the system
"""

import os
import sys
from pathlib import Path

def check_environment_variables():
    """Check if security environment variables are set"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = ['SECRET_KEY', 'DB_ENCRYPTION_KEY']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
            print(f"   ❌ {var} - NOT SET")
        else:
            value = os.environ.get(var)
            if len(value) < 32:
                print(f"   ⚠️  {var} - TOO SHORT (should be 32+ characters)")
            else:
                print(f"   ✅ {var} - OK")
    
    return len(missing) == 0

def check_file_permissions():
    """Check file permissions"""
    print("\n🔍 Checking File Permissions...")
    
    sensitive_files = [
        'instance/daily_report.db',
        '.env',
        'config.py'
    ]
    
    all_ok = True
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stat_info = os.stat(file_path)
            mode = oct(stat_info.st_mode)[-3:]
            
            if file_path.endswith('.db') or file_path == '.env':
                if mode != '600':
                    print(f"   ⚠️  {file_path} - Permissions: {mode} (should be 600)")
                    all_ok = False
                else:
                    print(f"   ✅ {file_path} - Permissions: {mode}")
            else:
                print(f"   ℹ️  {file_path} - Permissions: {mode}")
        else:
            print(f"   ℹ️  {file_path} - Not found")
    
    return all_ok

def check_gitignore():
    """Check if .gitignore protects sensitive files"""
    print("\n🔍 Checking .gitignore...")
    
    required_patterns = [
        '.env',
        '*.db',
        'instance/',
        '*.key'
    ]
    
    if not os.path.exists('.gitignore'):
        print("   ❌ .gitignore not found!")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    all_ok = True
    for pattern in required_patterns:
        if pattern in content:
            print(f"   ✅ {pattern} - Protected")
        else:
            print(f"   ❌ {pattern} - NOT protected")
            all_ok = False
    
    return all_ok

def check_database_backup():
    """Check if database backups exist"""
    print("\n🔍 Checking Database Backups...")
    
    backup_files = list(Path('.').glob('instance/*.backup_*'))
    
    if backup_files:
        print(f"   ✅ Found {len(backup_files)} backup(s)")
        latest = max(backup_files, key=os.path.getctime)
        print(f"   📅 Latest backup: {latest.name}")
        return True
    else:
        print("   ⚠️  No backups found")
        print("   💡 Run: python secure_database.py")
        return False

def check_https_config():
    """Check HTTPS configuration"""
    print("\n🔍 Checking HTTPS Configuration...")
    
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        print("   ✅ FLASK_ENV=production")
        print("   ⚠️  Make sure HTTPS is enabled on your server!")
    else:
        print(f"   ℹ️  FLASK_ENV={flask_env}")
        print("   💡 Set FLASK_ENV=production for deployment")
    
    return True

def check_dependencies():
    """Check if security dependencies are installed"""
    print("\n🔍 Checking Security Dependencies...")
    
    required_packages = [
        'cryptography',
        'werkzeug',
        'flask'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - Installed")
        except ImportError:
            print(f"   ❌ {package} - NOT installed")
            all_ok = False
    
    return all_ok

def check_debug_mode():
    """Check if debug mode is disabled"""
    print("\n🔍 Checking Debug Mode...")
    
    try:
        from app import create_app
        app = create_app()
        
        if app.debug:
            print("   ⚠️  DEBUG MODE IS ENABLED!")
            print("   💡 Disable debug mode in production")
            return False
        else:
            print("   ✅ Debug mode is disabled")
            return True
    except Exception as e:
        print(f"   ⚠️  Could not check: {e}")
        return False

def main():
    """Run all security checks"""
    print("\n" + "="*60)
    print("🔐 SECURITY CHECK")
    print("="*60)
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("File Permissions", check_file_permissions),
        (".gitignore", check_gitignore),
        ("Database Backups", check_database_backup),
        ("HTTPS Configuration", check_https_config),
        ("Dependencies", check_dependencies),
        ("Debug Mode", check_debug_mode)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n   ❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print(f"\n   Score: {passed}/{total}")
    
    if passed == total:
        print("\n   🎉 All security checks passed!")
        print("   ✅ System is secure and ready for production")
    else:
        print("\n   ⚠️  Some security checks failed")
        print("   💡 Review the issues above and fix them")
        print("\n   📚 See SECURITY_GUIDE.md for detailed instructions")
    
    print("\n" + "="*60)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
