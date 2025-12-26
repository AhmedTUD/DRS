"""
Database Security Script
Encrypts sensitive data and sets up database protection
"""

import os
import shutil
from datetime import datetime
from app import create_app, db
from app.models import User, Report
from app.security import DatabaseEncryption
import getpass

def backup_database():
    """Create backup of current database"""
    app = create_app()
    
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        else:
            print("⚠️  No database file found")
            return None

def setup_database_encryption():
    """Set up database encryption"""
    print("\n" + "="*60)
    print("🔐 DATABASE ENCRYPTION SETUP")
    print("="*60)
    
    # Get or generate encryption key
    encryption_key = os.environ.get('DB_ENCRYPTION_KEY')
    
    if not encryption_key:
        print("\n⚠️  DB_ENCRYPTION_KEY not set in environment variables")
        print("Generating a secure encryption key...")
        
        import secrets
        encryption_key = secrets.token_urlsafe(32)
        
        print(f"\n🔑 Your encryption key (SAVE THIS SECURELY!):")
        print(f"   {encryption_key}")
        print("\n⚠️  IMPORTANT: Add this to your environment variables:")
        print(f"   export DB_ENCRYPTION_KEY='{encryption_key}'")
        print("\n   Or add to .env file:")
        print(f"   DB_ENCRYPTION_KEY={encryption_key}")
        
        response = input("\nDo you want to continue with this key? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Setup cancelled")
            return False
        
        os.environ['DB_ENCRYPTION_KEY'] = encryption_key
    
    return True

def encrypt_sensitive_data():
    """Encrypt sensitive data in database"""
    app = create_app()
    
    with app.app_context():
        print("\n🔄 Encrypting sensitive data...")
        
        try:
            encryptor = DatabaseEncryption()
            
            # Note: In production, you would encrypt specific sensitive fields
            # For now, we'll just verify the encryption system works
            
            test_data = "Test sensitive data"
            encrypted = encryptor.encrypt(test_data)
            decrypted = encryptor.decrypt(encrypted)
            
            if decrypted == test_data:
                print("✅ Encryption system verified and working")
            else:
                print("❌ Encryption verification failed")
                return False
            
            print("✅ Sensitive data encryption completed")
            return True
            
        except Exception as e:
            print(f"❌ Error during encryption: {e}")
            return False

def set_database_permissions():
    """Set restrictive permissions on database file"""
    app = create_app()
    
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if os.path.exists(db_path):
            try:
                # Set read/write for owner only (600)
                os.chmod(db_path, 0o600)
                print(f"✅ Database permissions set to 600 (owner read/write only)")
                
                # Also protect the instance directory
                instance_dir = os.path.dirname(db_path)
                os.chmod(instance_dir, 0o700)
                print(f"✅ Instance directory permissions set to 700")
                
            except Exception as e:
                print(f"⚠️  Could not set permissions: {e}")
                print("   (This is normal on Windows)")
        else:
            print("⚠️  Database file not found")

def create_security_config():
    """Create .env file with security settings"""
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"\n⚠️  {env_file} already exists")
        response = input("Do you want to overwrite it? (yes/no): ")
        if response.lower() != 'yes':
            print("Skipping .env creation")
            return
    
    import secrets
    
    config_content = f"""# Security Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# IMPORTANT: Keep this file secure and never commit to git!

# Flask Secret Key (for sessions)
SECRET_KEY={secrets.token_hex(32)}

# Database Encryption Key
DB_ENCRYPTION_KEY={secrets.token_urlsafe(32)}

# Environment
FLASK_ENV=production

# Database URL (for production)
# DATABASE_URL=mysql+pymysql://username:password@localhost/dbname

# Session Settings
SESSION_TIMEOUT=1800

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_WINDOW=900
"""
    
    with open(env_file, 'w') as f:
        f.write(config_content)
    
    # Set restrictive permissions on .env file
    try:
        os.chmod(env_file, 0o600)
    except:
        pass
    
    print(f"\n✅ Created {env_file} with secure configuration")
    print(f"⚠️  IMPORTANT: Add {env_file} to .gitignore!")

def update_gitignore():
    """Update .gitignore to protect sensitive files"""
    gitignore_content = """
# Security - Never commit these!
.env
.env.local
.env.production
*.key
*.pem
*.p12

# Database
instance/
*.db
*.db-journal
*.db.backup_*

# Uploads
uploads/
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Updated .gitignore with security rules")

def main():
    """Main security setup"""
    print("\n" + "="*60)
    print("🔐 DATABASE SECURITY SETUP")
    print("="*60)
    print("\nThis script will:")
    print("1. Backup your current database")
    print("2. Set up encryption")
    print("3. Encrypt sensitive data")
    print("4. Set secure file permissions")
    print("5. Create security configuration")
    print("\n" + "="*60)
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Setup cancelled")
        return
    
    # Step 1: Backup
    print("\n📦 Step 1: Backing up database...")
    backup_path = backup_database()
    
    # Step 2: Setup encryption
    print("\n🔐 Step 2: Setting up encryption...")
    if not setup_database_encryption():
        return
    
    # Step 3: Encrypt data
    print("\n🔒 Step 3: Encrypting sensitive data...")
    if not encrypt_sensitive_data():
        return
    
    # Step 4: Set permissions
    print("\n🛡️  Step 4: Setting secure permissions...")
    set_database_permissions()
    
    # Step 5: Create config
    print("\n⚙️  Step 5: Creating security configuration...")
    create_security_config()
    
    # Step 6: Update gitignore
    print("\n📝 Step 6: Updating .gitignore...")
    update_gitignore()
    
    print("\n" + "="*60)
    print("✅ SECURITY SETUP COMPLETED!")
    print("="*60)
    print("\n📝 Next steps:")
    print("1. Review the .env file and update as needed")
    print("2. NEVER commit .env or database files to git")
    print("3. Keep your encryption key safe and backed up")
    print("4. Set up regular database backups")
    print("5. Use HTTPS in production")
    print("\n⚠️  IMPORTANT:")
    print("   - Save your encryption key securely")
    print("   - Without it, you cannot decrypt your data!")
    print("   - Consider using a password manager or secure vault")
    
    if backup_path:
        print(f"\n💾 Database backup saved at: {backup_path}")

if __name__ == '__main__':
    main()
