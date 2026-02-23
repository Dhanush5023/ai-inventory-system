import requests
import time
import sys

def run_tests():
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    max_retries = 5
    for i in range(max_retries):
        try:
            r = requests.get(f"{base_url}/health")
            if r.status_code == 200:
                print(f"Health check: {r.status_code}, {r.json()}")
                break
        except Exception:
            print(f"Server not ready, retrying ({i+1}/{max_retries})...")
            time.sleep(2)
    else:
        print("Server failed to start in time.")
        sys.exit(1)

    # Test root
    r = requests.get(f"{base_url}/")
    print(f"Root: {r.status_code}, {r.json()}")

    # Test API v1 health (if exists) or just some public endpoint
    # Let's try to get products - should be 401 Unauthorized if auth is working
    r = requests.get(f"{base_url}/api/v1/products")
    print(f"Get Products (Unauthorized check): {r.status_code}, {r.json()}")
    if r.status_code == 401:
        print("Auth check PASSED!")
    else:
        print("Auth check FAILED (expected 401)")

if __name__ == "__main__":
    run_tests()
