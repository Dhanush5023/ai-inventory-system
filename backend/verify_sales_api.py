import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_sales_refresh():
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@inventory.com", "password": "admin123"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get initial products
    print("Fetching products...")
    prod_res = requests.get(f"{BASE_URL}/products?limit=1", headers=headers)
    product = prod_res.json()["products"][0]
    print(f"Selected product: {product['name']} (ID: {product['id']})")

    # 3. Create a bulk sale
    print("Posting sale...")
    sale_payload = {
        "items": [
            {
                "product_id": product["id"],
                "quantity": 1,
                "unit_price": product["unit_price"],
                "notes": "Verification Script Sale"
            }
        ]
    }
    sale_res = requests.post(f"{BASE_URL}/sales/bulk", json=sale_payload, headers=headers)
    if sale_res.status_code != 201:
        print(f"Sale failed: {sale_res.text}")
        return
    new_sale_id = sale_res.json()[0]["id"]
    print(f"Sale created! ID: {new_sale_id}")

    # 4. Fetch sales list and check order
    print("Fetching sales list...")
    # Add a tiny delay like the frontend does
    time.sleep(0.5)
    list_res = requests.get(f"{BASE_URL}/sales?limit=5", headers=headers)
    sales = list_res.json()["sales"]
    
    if sales[0]["id"] == new_sale_id:
        print("SUCCESS: The newest sale is at the top of the list!")
    else:
        print(f"FAILURE: Newest sale {new_sale_id} not at top. Top is {sales[0]['id']}")

if __name__ == "__main__":
    test_sales_refresh()
