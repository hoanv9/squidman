
import sqlite3
import pickle
import shutil
import os
import sys
from datetime import datetime

# Configuration
OLD_DB_PATH = os.path.join('db', 'squid_manager-old.db')
NEW_DB_PATH = os.path.join('db', 'squid_manager.db')
BACKUP_PATH = f"{NEW_DB_PATH}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Schema Definitions for the NEW Structure
SCHEMAS = {
    "client": """
        CREATE TABLE IF NOT EXISTS "client" (
            id INTEGER PRIMARY KEY,
            ip_address TEXT NOT NULL UNIQUE,
            dns_hostname TEXT,
            ticket_id TEXT,
            expiration_date DATE NOT NULL,
            allowed_domains TEXT,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        );
    """,
    "global_domain_whitelist": """
        CREATE TABLE IF NOT EXISTS global_domain_whitelist (
            id INTEGER PRIMARY KEY,
            domain VARCHAR(255) NOT NULL UNIQUE,
            description VARCHAR(255),
            date_added DATETIME
        );
    """,
    "global_ip_whitelist": """
        CREATE TABLE IF NOT EXISTS global_ip_whitelist (
            id INTEGER PRIMARY KEY,
            ip_address VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(255),
            date_added DATETIME
        );
    """,
    "domain_templates": """
        CREATE TABLE IF NOT EXISTS domain_templates (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            domains TEXT NOT NULL,
            description VARCHAR(255),
            date_created DATETIME,
            date_modified DATETIME
        );
    """
}

def ensure_schema(conn):
    """Ensures all required tables exist in the new database."""
    print("Verifying/Creating schema...")
    cur = conn.cursor()
    for table_name, schema_sql in SCHEMAS.items():
        try:
            print(f" - Checking table: {table_name}")
            cur.execute(schema_sql)
        except sqlite3.Error as e:
            print(f"Error creating table {table_name}: {e}")
            raise
    conn.commit()

def migrate_db():
    print("Starting migration process...")
    
    # 1. Validation
    if not os.path.exists(OLD_DB_PATH):
        print(f"Error: Old database not found at {OLD_DB_PATH}")
        return
    
    # NEW: Create empty DB file if it doesn't exist, so we can connect to it
    if not os.path.exists(NEW_DB_PATH):
        print(f"New database not found. Creating new empty DB at {NEW_DB_PATH}")
        # Just touching the file is enough, sqlite3.connect will create header
    
    # 2. Backup (only if it exists and has content)
    if os.path.exists(NEW_DB_PATH) and os.path.getsize(NEW_DB_PATH) > 0:
        try:
            shutil.copy(NEW_DB_PATH, BACKUP_PATH)
            print(f"Created backup of existing new database at: {BACKUP_PATH}")
        except Exception as e:
            print(f"Error creating backup: {e}")
            return

    # 3. Connection & Schema Setup
    try:
        old_conn = sqlite3.connect(OLD_DB_PATH)
        old_conn.row_factory = sqlite3.Row
        
        new_conn = sqlite3.connect(NEW_DB_PATH)
        
        # --- ENSURE SCHEMA EXISTS ---
        ensure_schema(new_conn)
        # ----------------------------

        old_cur = old_conn.cursor()
        new_cur = new_conn.cursor()
        
        # 4. Read from OLD DB
        print(f"Reading data from {OLD_DB_PATH}...")
        
        columns = [
            'id', 'ip_address', 'dns_hostname', 'ticket_id', 
            'expiration_date', 'allowed_domains', 'date_added', 'notes'
        ]
        
        # Check if table exists in old db
        try:
            old_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='client'")
            if not old_cur.fetchone():
                 print("Table 'client' not found in old DB. Checking 'Client_old'...")
                 # Fallback logic if needed, but earlier we saw 'client' exists
        except:
            pass

        query = f"SELECT {', '.join(columns)} FROM client"
        rows = old_cur.execute(query).fetchall()
        
        print(f"Found {len(rows)} clients to migrate.")
        
        migrated_count = 0
        
        # 5. Transform and Insert
        for row in rows:
            data = dict(row)
            
            # --- Transformation Logic ---
            raw_domains = data['allowed_domains']
            converted_domains = ""
            
            if isinstance(raw_domains, bytes):
                try:
                    domain_list = pickle.loads(raw_domains)
                    if isinstance(domain_list, list):
                        converted_domains = "\n".join([d for d in domain_list if d])
                    else:
                        converted_domains = str(domain_list)
                except Exception as e:
                    print(f"Warning: Failed to unpickle domains for ID {data['id']}: {e}")
                    converted_domains = str(raw_domains)
            elif isinstance(raw_domains, str):
                converted_domains = raw_domains
            else:
                converted_domains = "" if raw_domains is None else str(raw_domains)
            
            data['allowed_domains'] = converted_domains
            
            # Prepare INSERT query
            placeholders = ", ".join(["?"] * len(columns))
            insert_sql = f"""
                INSERT OR REPLACE INTO client ({', '.join(columns)}) 
                VALUES ({placeholders})
            """
            
            values = tuple(data[col] for col in columns)
            new_cur.execute(insert_sql, values)
            migrated_count += 1
            
        new_conn.commit()
        print(f"Success! Migrated {migrated_count} records.")
        print("Schema verified and all tables created.")
        
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        if 'new_conn' in locals():
            new_conn.rollback()
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'old_conn' in locals(): old_conn.close()
        if 'new_conn' in locals(): new_conn.close()

if __name__ == "__main__":
    migrate_db()
