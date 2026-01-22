"""
Database Migration Script - Add Repository Type and Signing Request

This script adds new fields to support:
1. Repository type (PERSONAL/CLASS/DEPARTMENT)
2. Process status (malware scanning)
3. System-generated folders
4. Signing request workflow

Run this script AFTER backing up the database.
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Execute migration to add new fields and tables."""
    
    # Get database path
    db_path = Path(__file__).parent.parent / "drive.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🔄 Starting migration on {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ===== Step 1: Add new fields to drive_items =====
        print("\n📝 Step 1: Adding new fields to drive_items table...")
        
        # Add repository_type (default PERSONAL)
        cursor.execute("""
            ALTER TABLE drive_items 
            ADD COLUMN repository_type TEXT DEFAULT 'PERSONAL' NOT NULL
        """)
        print("  ✅ Added repository_type")
        
        # Add repository_context_id (nullable)
        cursor.execute("""
            ALTER TABLE drive_items 
            ADD COLUMN repository_context_id INTEGER
        """)
        print("  ✅ Added repository_context_id")
        
        # Add owner_type (default based on existing user role)
        # We'll set this to 'LECTURER' temporarily, then update based on users table
        cursor.execute("""
            ALTER TABLE drive_items 
            ADD COLUMN owner_type TEXT DEFAULT 'LECTURER' NOT NULL
        """)
        print("  ✅ Added owner_type")
        
        # Add process_status (default READY for existing files)
        cursor.execute("""
            ALTER TABLE drive_items 
            ADD COLUMN process_status TEXT DEFAULT 'READY' NOT NULL
        """)
        print("  ✅ Added process_status")
        
        # Add is_system_generated
        cursor.execute("""
            ALTER TABLE drive_items 
            ADD COLUMN is_system_generated INTEGER DEFAULT 0 NOT NULL
        """)
        print("  ✅ Added is_system_generated")
        
        # Add is_locked
        cursor.execute("""
            ALTER TABLE drive_items 
            ADD COLUMN is_locked INTEGER DEFAULT 0 NOT NULL
        """)
        print("  ✅ Added is_locked")
        
        # ===== Step 2: Update owner_type based on user role =====
        print("\n📝 Step 2: Updating owner_type from user roles...")
        cursor.execute("""
            UPDATE drive_items 
            SET owner_type = (
                SELECT CASE 
                    WHEN u.role = 'ADMIN' THEN 'ADMIN'
                    WHEN u.role = 'TEACHER' THEN 'LECTURER'
                    WHEN u.role = 'STUDENT' THEN 'STUDENT'
                    ELSE 'LECTURER'
                END
                FROM users u 
                WHERE u.user_id = drive_items.owner_id
            )
        """)
        updated_count = cursor.rowcount
        print(f"  ✅ Updated {updated_count} rows")
        
        # ===== Step 3: Create signing_requests table =====
        print("\n📝 Step 3: Creating signing_requests table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signing_requests (
                request_id TEXT PRIMARY KEY,
                drive_item_id TEXT NOT NULL,
                requester_id INTEGER NOT NULL,
                approver_id INTEGER,
                current_status TEXT DEFAULT 'DRAFT' NOT NULL,
                admin_comment TEXT,
                signed_file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                approved_at TIMESTAMP,
                FOREIGN KEY (drive_item_id) REFERENCES drive_items(item_id) ON DELETE CASCADE,
                FOREIGN KEY (requester_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (approver_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """)
        print("  ✅ Created signing_requests table")
        
        # ===== Step 4: Create indexes for performance =====
        print("\n📝 Step 4: Creating indexes...")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_drive_items_repository 
            ON drive_items(repository_type, repository_context_id)
        """)
        print("  ✅ Created index on repository_type/repository_context_id")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_drive_items_process_status 
            ON drive_items(process_status)
        """)
        print("  ✅ Created index on process_status")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signing_requests_status 
            ON signing_requests(current_status)
        """)
        print("  ✅ Created index on signing_requests.current_status")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signing_requests_requester 
            ON signing_requests(requester_id)
        """)
        print("  ✅ Created index on signing_requests.requester_id")
        
        # Commit all changes
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Final schema verification...")
        
        # Verify new fields
        cursor.execute("PRAGMA table_info(drive_items)")
        columns = cursor.fetchall()
        print(f"\n  drive_items table now has {len(columns)} columns:")
        for col in columns:
            if col[1] in ['repository_type', 'repository_context_id', 'owner_type', 
                          'process_status', 'is_system_generated', 'is_locked']:
                print(f"    ✅ {col[1]} ({col[2]})")
        
        # Verify signing_requests table
        cursor.execute("PRAGMA table_info(signing_requests)")
        sr_columns = cursor.fetchall()
        print(f"\n  signing_requests table has {len(sr_columns)} columns")
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_backup_exists():
    """Check if backup file exists before running migration."""
    backup_path = Path(__file__).parent.parent / "backup_before_repo_type.sql"
    
    if not backup_path.exists():
        print("⚠️  WARNING: Backup file not found!")
        print(f"   Expected: {backup_path}")
        print("\n   Please create backup first:")
        print("   cd hpc_drive && sqlite3 drive.db \".backup backup_before_repo_type.sql\"")
        return False
    
    print(f"✅ Backup file found: {backup_path}")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("  Database Migration: Repository Type & Signing Request")
    print("=" * 60)
    
    # Check backup
    if not verify_backup_exists():
        print("\n❌ Migration aborted. Create backup first.")
        exit(1)
    
    # Run migration
    print("\nProceed with migration? (yes/no): ", end="")
    confirm = input().strip().lower().replace('"', '').replace("'", "")

    if confirm not in ("y", "yes"):
        print("❌ Migration cancelled by user.")
        exit(0)
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("  ✅ Migration completed successfully!")
        print("=" * 60)
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("  ❌ Migration failed!")
        print("=" * 60)
        exit(1)
