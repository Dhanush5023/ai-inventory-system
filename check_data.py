from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Setup DB connection to the backend's sqlite file
# Assuming we run this from project root
db_path = "sqlite:///./backend/inventory.db"
engine = create_engine(db_path)
Session = sessionmaker(bind=engine)
session = Session()

try:
    print(f"Checking data integrity in {db_path}...")
    
    # Check 1: Products with NULL cost_price
    result = session.execute(text("SELECT id, name FROM products WHERE cost_price IS NULL")).fetchall()
    if result:
        print(f"[FAIL] Found {len(result)} products with NULL cost_price:")
        for r in result:
            print(f" - ID {r[0]}: {r[1]}")
    else:
        print("[PASS] No products with NULL cost_price.")

    # Check 2: Products with NULL supplier_id
    # (This assumes supplier_id should not be NULL, though po_agent handles it by skipping. 
    # But good to know)
    result = session.execute(text("SELECT id, name FROM products WHERE supplier_id IS NULL")).fetchall()
    if result:
        print(f"[INFO] Found {len(result)} products with NULL supplier_id (po_agent should skip them):")
        # for r in result:
        #    print(f" - ID {r[0]}: {r[1]}")
    else:
        print("[PASS] All products have a supplier_id.")

    # Check 3: Products with invalid stock (None)
    result = session.execute(text("SELECT id, name FROM products WHERE current_stock IS NULL")).fetchall()
    if result:
        print(f"[FAIL] Found {len(result)} products with NULL current_stock:")
        for r in result:
             print(f" - ID {r[0]}: {r[1]}")
    else:
        print("[PASS] No products with NULL current_stock.")

    # Check 4: Check if any sales exist (for Avg Daily Demand calc)
    result = session.execute(text("SELECT count(*) FROM sales")).scalar()
    print(f"[INFO] Total sales records: {result}")

except Exception as e:
    print(f"[ERROR] Script failed: {e}")
finally:
    session.close()
