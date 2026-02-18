import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def benchmark_analytics():
    print("Benchmarking Optimized Analytics API...")
    
    # 1. Login to get token
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@inventory.com",
        "password": "admin123"
    })
    
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Measure Analytics API
    start_time = time.time()
    res = requests.get(f"{BASE_URL}/analytics", headers=headers)
    end_time = time.time()
    
    execution_time = (end_time - start_time) * 1000
    
    if res.status_code == 200:
        print(f"✅ Success! Analytics API responded in {execution_time:.2f}ms")
        # print(json.dumps(res.json(), indent=2))
    else:
        print(f"❌ Failed: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    benchmark_analytics()
