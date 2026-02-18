import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def diag():
    print("--- Granular Diagnostics ---")
    
    # 1. Root / Health
    try:
        start = time.time()
        res = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"Root: {res.status_code} in {(time.time()-start)*1000:.2f}ms")
    except Exception as e:
        print(f"Root failed: {e}")

    # 2. Login
    token = None
    try:
        print("Testing Login...")
        start = time.time()
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@inventory.com",
            "password": "admin123"
        }, timeout=10)
        print(f"Login: {res.status_code} in {(time.time()-start)*1000:.2f}ms")
        if res.status_code == 200:
            token = res.json().get("access_token")
    except Exception as e:
        print(f"Login failed: {e}")

    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Auth Me (Multiple times)
    print("Testing /auth/me (5 iterations)...")
    for i in range(5):
        try:
            start = time.time()
            res = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            print(f"  [{i+1}] Auth Me: {res.status_code} in {(time.time()-start)*1000:.2f}ms")
        except Exception as e:
            print(f"  [{i+1}] Auth Me failed: {e}")

    # 4. Analytics
    try:
        print("Testing /analytics...")
        start = time.time()
        res = requests.get(f"{BASE_URL}/analytics", headers=headers, timeout=10)
        print(f"Analytics: {res.status_code} in {(time.time()-start)*1000:.2f}ms")
    except Exception as e:
        print(f"Analytics failed: {e}")

    # 5. Top Products
    try:
        print("Testing /sales/stats/top-products...")
        start = time.time()
        res = requests.get(f"{BASE_URL}/sales/stats/top-products?limit=5", headers=headers, timeout=10)
        print(f"Top Products: {res.status_code} in {(time.time()-start)*1000:.2f}ms")
    except Exception as e:
        print(f"Top Products failed: {e}")

    # 6. Alerts
    try:
        print("Testing /alerts...")
        start = time.time()
        res = requests.get(f"{BASE_URL}/alerts?unresolved_only=true&limit=3", headers=headers, timeout=10)
        print(f"Alerts: {res.status_code} in {(time.time()-start)*1000:.2f}ms")
    except Exception as e:
        print(f"Alerts failed: {e}")

if __name__ == "__main__":
    diag()
