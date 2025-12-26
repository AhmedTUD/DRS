"""
Update database schema for security features
"""

from app import create_app, db
from sqlalchemy import text

def update_database_security():
    app = create_app()
    
    with app.app_context():
        print("🔄 Updating database for security features...")
        
        try:
            # Create all new tables
            db.create_all()
            print("✅ Created new tables")
            
            # Check if AuditLog table exists
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"))
                if result.fetchone():
                    print("✅ AuditLog table exists")
                else:
                    print("⚠️  AuditLog table not found, creating...")
                    db.create_all()
            
            print("\n✅ Security database update completed!")
            print("\n📝 Summary:")
            print("   - AuditLog table: Created/Verified")
            print("   - Security features: Ready")
            print("\n🚀 You can now use the enhanced security features!")
            
        except Exception as e:
            print(f"\n❌ Error updating database: {e}")
            print("\nIf you're using MySQL/PostgreSQL, you may need to run:")
            print("   CREATE TABLE audit_log (")
            print("       id INTEGER PRIMARY KEY AUTO_INCREMENT,")
            print("       event_type VARCHAR(50) NOT NULL,")
            print("       user_id INTEGER,")
            print("       details TEXT,")
            print("       ip_address VARCHAR(45),")
            print("       user_agent VARCHAR(200),")
            print("       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,")
            print("       FOREIGN KEY (user_id) REFERENCES user(id)")
            print("   );")

if __name__ == '__main__':
    update_database_security()
