"""
Migration script to add comments, notifications, and report status features
Run this script to update your database schema
"""

from app import create_app, db
from app.models import Report, ReportComment, Notification

def upgrade():
    """Add new tables and columns"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        
        # Create all new tables
        db.create_all()
        print("✅ Created new tables: ReportComment, Notification")
        
        # Add new columns to Report table if they don't exist
        try:
            # Check if columns exist by trying to query them
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('report')]
            
            if 'status' not in columns:
                print("⚠️  Column 'status' not found in Report table")
                print("   Please add manually: ALTER TABLE report ADD COLUMN status VARCHAR(20) DEFAULT 'new' NOT NULL;")
            else:
                print("✅ Column 'status' already exists")
            
            if 'is_read' not in columns:
                print("⚠️  Column 'is_read' not found in Report table")
                print("   Please add manually: ALTER TABLE report ADD COLUMN is_read BOOLEAN DEFAULT 0;")
            else:
                print("✅ Column 'is_read' already exists")
                
        except Exception as e:
            print(f"❌ Error checking columns: {e}")
        
        print("✅ Migration completed!")
        print("\n📝 Next steps:")
        print("   1. If you see warnings above, run the ALTER TABLE commands manually")
        print("   2. Restart your application")
        print("   3. Test the new features")

if __name__ == '__main__':
    upgrade()
