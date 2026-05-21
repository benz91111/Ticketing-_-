"""
Backup System
"""
import shutil
import datetime
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "databases" / "tickets.db"
BACKUPS_DIR = BASE_DIR / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)

def create_backup():
    """Create a database backup"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUPS_DIR / f"backup_{timestamp}.db"

    shutil.copy2(DB_PATH, backup_file)
    size = backup_file.stat().st_size

    # Save to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO backups (filename, size_bytes) VALUES (?, ?)", (str(backup_file.name), size))
    conn.commit()
    conn.close()

    return str(backup_file), size

def cleanup_old_backups(max_backups=10):
    """Remove old backups"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filename FROM backups ORDER BY created_at DESC LIMIT -1 OFFSET ?", (max_backups,))
    for row in c.fetchall():
        old_file = BACKUPS_DIR / row[1]
        if old_file.exists():
            old_file.unlink()
        c.execute("DELETE FROM backups WHERE id = ?", (row[0],))
    conn.commit()
    conn.close()

def get_backups():
    """Get all backups"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM backups ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows
