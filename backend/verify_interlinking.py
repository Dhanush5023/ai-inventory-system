import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def verify_interlinking():
    print("\n--- Verifying Customer-Admin Interlinking ---")
    
    # 1. Login as Admin to check initial state
    admin_session = requests.Session()
    admin_login = admin_session.post(f"{BASE_URL}/auth/login", json={"email": "admin@inventory.com", "password": "admin123"})
    admin_token = admin_login.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get initial sales count and a product stock
    initial_sales = admin_session.get(f"{BASE_URL}/sales", headers=admin_headers).json().get("total", 0)
    products = admin_session.get(f"{BASE_URL}/products", params={"limit": 1}, headers=admin_headers).json().get("products", [])
    if not products:
        print("FAILED: No products found for testing")
        return
    
    test_product = products[0]
    initial_stock = test_product["current_stock"]
    print(f"Initial State: Sales Count = {initial_sales}, Stock for {test_product['name']} = {initial_stock}")
    
    # 2. Login as Customer and perform a "Buy Now"
    cust_session = requests.Session()
    cust_login = cust_session.post(f"{BASE_URL}/auth/login", json={"email": "customer@inventory.com", "password": "customer123"})
    cust_token = cust_login.json().get("access_token")
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    
    print(f"Customer purchasing 1 unit of {test_product['name']}...")
    buy_res = cust_session.post(f"{BASE_URL}/sales", json={
        "product_id": test_product["id"],
        "quantity": 1,
        "unit_price": test_product["unit_price"],
        "notes": "Interlinking verification purchase"
    }, headers=cust_headers)
    
    if buy_res.status_code != 201:
        print(f"FAILED: Purchase failed with status {buy_res.status_code}. Response: {buy_res.text}")
        return
    
    print("PASSED: Customer purchase recorded")
    
    # 3. Verify Admin sees the updated data
    time.sleep(1) # Give a moment for DB sync
    final_sales = admin_session.get(f"{BASE_URL}/sales", headers=admin_headers).json().get("total", 0)
    p_after = admin_session.get(f"{BASE_URL}/products/{test_product['id']}", headers=admin_headers).json()
    final_stock = p_after["current_stock"]
    
    print(f"Final State: Sales Count = {final_sales}, Stock for {test_product['name']} = {final_stock}")
    
    if final_sales == initial_sales + 1 and final_stock == initial_stock - 1:
        print("\nSUCCESS: Customer-Admin interlinking is working perfectly!")
        print("- Sale appeared in Admin's list")
        print("- Stock was deducted from Admin's inventory")
    else:
        print("\nFAILED: Data synchronization failed")
        if final_sales != initial_sales + 1:
            print(f"Expected sales count {initial_sales + 1}, got {final_sales}")
        if final_stock != initial_stock - 1:
            print(f"Expected stock {initial_stock - 1}, got {final_stock}")

if __name__ == "__main__":
    verify_interlinking()
