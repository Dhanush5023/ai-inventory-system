import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_role_flow(email, password, role_name):
    print(f"\n--- Testing {role_name} Flow ({email}) ---")
    session = requests.Session()
    
    # 1. Login
    login_res = session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if login_res.status_code != 200:
        print(f"FAILED: Login failed for {role_name}. Status: {login_res.status_code}")
        return None
    
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"PASSED: Login successful for {role_name}")

    # 2. Check /me
    me_res = session.get(f"{BASE_URL}/auth/me", headers=headers)
    user_data = me_res.json()
    print(f"PASSED: User role verified as: {user_data.get('role')}")

    # 3. Test access to restricted endpoints
    # Customers should NOT access /analytics
    analytics_res = session.get(f"{BASE_URL}/analytics", headers=headers)
    if role_name == "Customer":
        if analytics_res.status_code == 403 or analytics_res.status_code == 401:
            print("PASSED: Customer correctly denied access to analytics")
        else:
             print(f"FAILED: Customer access to analytics returned {analytics_res.status_code}")
    else:
        if analytics_res.status_code == 200:
            print(f"PASSED: {role_name} correctly granted access to analytics")
        else:
            print(f"FAILED: {role_name} denied access to analytics. Status: {analytics_res.status_code}")

    # 4. Test "Buy Now" flow for Customer
    if role_name == "Customer":
        # Get a product
        products_res = session.get(f"{BASE_URL}/products", params={"limit": 1}, headers=headers)
        product = products_res.json().get("products", [])[0]
        print(f"Testing 'Buy Now' for: {product['name']} (Stock: {product['current_stock']})")
        
        sale_data = {
            "product_id": product['id'],
            "quantity": 1,
            "unit_price": product['unit_price'],
            "notes": "Verification test purchase"
        }
        
        buy_res = session.post(f"{BASE_URL}/sales", json=sale_data, headers=headers)
        if buy_res.status_code == 201:
            print("PASSED: Purchase successful")
            # Verify stock deduction
            p_after = session.get(f"{BASE_URL}/products/{product['id']}", headers=headers).json()
            if p_after['current_stock'] == product['current_stock'] - 1:
                print(f"PASSED: Stock correctly deducted ({p_after['current_stock']})")
            else:
                print(f"FAILED: Stock not deducted correctly. Got {p_after['current_stock']}")
        else:
            print(f"FAILED: Purchase failed. Status: {buy_res.status_code}, {buy_res.text}")

    return token

if __name__ == "__main__":
    # Test Admin
    test_role_flow("admin@inventory.com", "admin123", "Admin")
    # Test Customer
    test_role_flow("customer@inventory.com", "customer123", "Customer")
    # Test Manager (Staff role in this system is 'manager')
    test_role_flow("manager@inventory.com", "manager123", "Manager")
