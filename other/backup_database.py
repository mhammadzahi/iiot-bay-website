#!/usr/bin/env python3
"""
Database Backup Tool
====================
Creates a timestamped backup of the SQLite database before making changes.

Usage:
    python backup_database.py
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'iiot_bay_database.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')


def create_backup() -> str:
    """Create a timestamped backup of the database"""
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return None
    
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'iiot_bay_database_backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Copy database file
    try:
        shutil.copy2(DB_PATH, backup_path)
        file_size = os.path.getsize(backup_path)
        print(f"✓ Backup created successfully:")
        print(f"  File: {backup_path}")
        print(f"  Size: {file_size / 1024:.2f} KB")
        
        # Verify backup integrity
        conn = sqlite3.connect(backup_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM posts")
        post_count = cur.fetchone()[0]
        conn.close()
        
        print(f"  Posts: {post_count}")
        print(f"\nBackup verified and ready.")
        
        return backup_path
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None


def list_backups():
    """List all available backups"""
    if not os.path.exists(BACKUP_DIR):
        print("No backups directory found.")
        return
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
    
    if not backups:
        print("No backups found.")
        return
    
    print(f"\nAvailable backups ({len(backups)}):")
    print("-" * 80)
    
    for backup in sorted(backups, reverse=True):
        backup_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(backup_path)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
        print(f"{backup}")
        print(f"  Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Size: {size / 1024:.2f} KB")


def restore_backup(backup_filename: str) -> bool:
    """Restore a backup"""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"Error: Backup file not found: {backup_path}")
        return False
    
    # Create a backup of current database first
    print("Creating safety backup of current database...")
    safety_backup = create_backup()
    
    if not safety_backup:
        print("Failed to create safety backup. Aborting restore.")
        return False
    
    try:
        # Restore the backup
        shutil.copy2(backup_path, DB_PATH)
        print(f"\n✓ Database restored from: {backup_filename}")
        print(f"  Safety backup saved at: {safety_backup}")
        return True
    except Exception as e:
        print(f"Error restoring backup: {e}")
        return False


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup and restore database')
    parser.add_argument('--list', action='store_true', help='List all backups')
    parser.add_argument('--restore', type=str, help='Restore a specific backup by filename')
    args = parser.parse_args()
    
    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(args.restore)
    else:
        # Default action: create backup
        create_backup()


if __name__ == '__main__':
    main()
