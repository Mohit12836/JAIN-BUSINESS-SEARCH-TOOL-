"""
Persistent SQLite History Database for JainBiz Lead Miner.
Ensures that previously extracted firms and phone numbers are remembered permanently
across PC restarts, so duplicate businesses are never re-scraped.
"""

import sqlite3
import os
import re
from typing import Dict, Any

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "database")
DB_PATH = os.path.join(DB_DIR, "leads_history.db")

def init_db():
    """Initializes the persistent leads history table."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            name_norm TEXT,
            firm_name TEXT,
            city TEXT,
            category TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone ON scraped_leads (phone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name_norm ON scraped_leads (name_norm)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT UNIQUE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            city TEXT,
            area_name TEXT,
            batch_size INTEGER,
            extracted_count INTEGER,
            cumulative_total INTEGER,
            status TEXT DEFAULT 'Completed',
            next_area TEXT,
            sync_status TEXT DEFAULT 'Synced'
        )
    """)
    conn.commit()
    conn.close()

def normalize_key(text: str) -> str:
    """Creates a normalized alphanumeric string for deduplication."""
    if not text:
        return ""
    return re.sub(r"[^a-zA-Z0-9]", "", text.lower())

def is_already_scraped(phone: str, firm_name: str) -> bool:
    """Checks if a firm or phone number has already been scraped in any previous session."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    clean_digits = re.sub(r"\D", "", phone) if phone and phone != "Not Listed" else ""
    norm_name = normalize_key(firm_name)
    
    # 1. Check by phone number (strongest check)
    if clean_digits and len(clean_digits) >= 10:
        cursor.execute("SELECT id FROM scraped_leads WHERE phone = ?", (clean_digits[-10:],))
        if cursor.fetchone():
            conn.close()
            return True

    # 2. Check by normalized firm name
    if norm_name:
        cursor.execute("SELECT id FROM scraped_leads WHERE name_norm = ?", (norm_name,))
        if cursor.fetchone():
            conn.close()
            return True

    conn.close()
    return False

def save_scraped_lead(record: Dict[str, Any]):
    """Permanently records a scraped lead into the SQLite database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    phone_raw = record.get("phone", "")
    clean_digits = re.sub(r"\D", "", phone_raw) if phone_raw and phone_raw != "Not Listed" else ""
    phone_key = clean_digits[-10:] if len(clean_digits) >= 10 else f"nophone_{normalize_key(record.get('name', ''))[:20]}"
    norm_name = normalize_key(record.get("name", ""))

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO scraped_leads (phone, name_norm, firm_name, city, category)
            VALUES (?, ?, ?, ?, ?)
        """, (
            phone_key,
            norm_name,
            record.get("name", ""),
            record.get("city", ""),
            record.get("j4j_category", "")
        ))
        conn.commit()
    except Exception as e:
        print(f"Database save error: {e}")
    finally:
        conn.close()

def get_history_count() -> int:
    """Returns total number of unique leads saved across all time."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scraped_leads")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def record_search_batch(
    batch_id: str,
    category: str,
    city: str,
    area_name: str,
    batch_size: int,
    extracted_count: int,
    next_area: str,
    status: str = "Completed",
    sync_status: str = "Synced"
) -> int:
    """Records a completed search batch for full historical tracking."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scraped_leads")
    cum_total = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT OR REPLACE INTO search_batches 
        (batch_id, category, city, area_name, batch_size, extracted_count, cumulative_total, status, next_area, sync_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        batch_id,
        category,
        city,
        area_name,
        batch_size,
        extracted_count,
        cum_total,
        status,
        next_area,
        sync_status
    ))
    conn.commit()
    conn.close()
    return cum_total

def get_search_history() -> list:
    """Returns all recorded search batches ordered chronologically."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_batches ORDER BY id ASC")
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history

