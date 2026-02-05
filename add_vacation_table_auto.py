#!/usr/bin/env python3
"""
Auto Migration Script to add Vacation table to existing database
This script will find the database automatically and add the vacation table
"""

import sqlite3
import os
import sys
from pathlib import Path

def find_database():
    """Find the daily_report.db file in common locations"""
    possible_paths = [
        'instance/daily_report.db',
        './instance/daily_report.db',
        '../instance/daily_report.db',
        'daily_report.db',
        './daily_report.db'
    ]
    
    # Search in current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'daily_report.db':
                possible_paths.append(os.path.join(root, file))
    
    # Check each possible path
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found database at: {path}")
            return path
    
    return None

def check_existing_tables(db_path):
    """Check what tables already exist in the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []

def create_backup(db_path):
    """Create a backup of the database before making changes"""
    try:
        import shutil
        from datetime import datetime
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
        return None

def add_vacation_table(db_path):
    """Add vacation table to the database"""
    try:
        # Create backup first
        backup_path = create_backup(db_path)
        if backup_path:
            print("🛡️  Database backup created for safety")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if vacation table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vacation'")
        if cursor.fetchone():
            print("✅ Vacation table already exists!")
            conn.close()
            return True
        
        print("🔄 Creating vacation table...")
        
        # Create vacation table (IF NOT EXISTS for extra safety)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                vacation_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
                UNIQUE(user_id, vacation_date)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Vacation table created successfully!")
        print("🛡️  All existing data is safe and untouched!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if backup_path and os.path.exists(backup_path):
            print(f"🔄 You can restore from backup: {backup_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if backup_path and os.path.exists(backup_path):
            print(f"🔄 You can restore from backup: {backup_path}")
        return False

def verify_vacation_table(db_path):
    """Verify that the vacation table was created correctly"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(vacation)")
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ Vacation table not found!")
            return False
        
        print("\n📊 Vacation table structure:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check if table has the right structure
        expected_columns = ['id', 'user_id', 'vacation_date', 'created_at']
        actual_columns = [col[1] for col in columns]
        
        if all(col in actual_columns for col in expected_columns):
            print("✅ Table structure is correct!")
        else:
            print("⚠️  Table structure might be incomplete")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False

def main():
    print("🏖️  Auto Migration: Adding Vacation Table")
    print("=" * 50)
    
    # Find the database
    db_path = find_database()
    if not db_path:
        print("❌ Could not find daily_report.db file!")
        print("Make sure you're running this script from the project directory")
        sys.exit(1)
    
    # Show existing tables
    existing_tables = check_existing_tables(db_path)
    if existing_tables:
        print(f"📋 Existing tables: {', '.join(existing_tables)}")
    else:
        print("⚠️  Could not read existing tables")
    
    # Add vacation table
    if add_vacation_table(db_path):
        # Verify the table
        if verify_vacation_table(db_path):
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Update your application code")
            print("2. Restart your Docker containers")
            print("3. Test the vacation functionality")
        else:
            print("\n⚠️  Migration completed but verification failed")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()