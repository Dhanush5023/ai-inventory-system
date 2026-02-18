import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_order():
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@inventory.com", "password": "admin123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    list_res = requests.get(f"{BASE_URL}/sales?limit=5", headers=headers)
    sales = list_res.json()["sales"]
    
    print("Top 5 sales in list:")
    for s in sales:
        print(f"ID: {s['id']}, Date: {s['sale_date']}, Product: {s['product_name']}")

if __name__ == "__main__":
    debug_order()
