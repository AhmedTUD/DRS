"""
Database Update Script
Run this to add new columns and tables for comments and notifications system
"""

from app import create_app, db
from sqlalchemy import text

def update_database():
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database update...")
        
        try:
            # Create all new tables (ReportComment, Notification)
            db.create_all()
            print("✅ Created new tables")
            
            # Add new columns to Report table
            with db.engine.connect() as conn:
                # Check if columns exist
                result = conn.execute(text("PRAGMA table_info(report)"))
                columns = [row[1] for row in result]
                
                if 'status' not in columns:
                    print("➕ Adding 'status' column to Report table...")
                    conn.execute(text("ALTER TABLE report ADD COLUMN status VARCHAR(20) DEFAULT 'new' NOT NULL"))
                    conn.commit()
                    print("✅ Added 'status' column")
                else:
                    print("ℹ️  Column 'status' already exists")
                
                if 'is_read' not in columns:
                    print("➕ Adding 'is_read' column to Report table...")
                    conn.execute(text("ALTER TABLE report ADD COLUMN is_read BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("✅ Added 'is_read' column")
                else:
                    print("ℹ️  Column 'is_read' already exists")
            
            print("\n✅ Database update completed successfully!")
            print("\n📝 Summary:")
            print("   - ReportComment table: Created")
            print("   - Notification table: Created")
            print("   - Report.status column: Added")
            print("   - Report.is_read column: Added")
            print("\n🚀 You can now restart your application!")
            
        except Exception as e:
            print(f"\n❌ Error updating database: {e}")
            print("\nIf you're using MySQL/PostgreSQL, you may need to run these SQL commands manually:")
            print("   ALTER TABLE report ADD COLUMN status VARCHAR(20) DEFAULT 'new' NOT NULL;")
            print("   ALTER TABLE report ADD COLUMN is_read BOOLEAN DEFAULT FALSE;")

if __name__ == '__main__':
    update_database()
