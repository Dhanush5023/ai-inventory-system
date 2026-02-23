import sqlite3
import os

db_path = "c:/Users/LENOVO/Downloads/ai-inventory-system/backend/inventory.db"
print(f"Checking DB at {db_path}...")

try:
    if not os.path.exists(db_path):
        print("DB file does not exist!")
    else:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        print("Attempting to read from 'users' table...")
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"Success! Found {count} users.")
        conn.close()
except Exception as e:
    print(f"Error accessing DB: {e}")
