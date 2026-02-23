import requests
import time

url = "http://127.0.0.1:8000/api/v1/auth/me"
print(f"Testing {url} with NO token (should be 401)...")

start = time.time()
try:
    response = requests.get(url, timeout=5)
    end = time.time()
    print(f"Status: {response.status_code}")
    print(f"Time: {end - start:.4f}s")
    print(f"Response: {response.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

url_health = "http://127.0.0.1:8000/health"
print(f"\nTesting {url_health}...")
start = time.time()
try:
    response = requests.get(url_health, timeout=5)
    end = time.time()
    print(f"Status: {response.status_code}")
    print(f"Time: {end - start:.4f}s")
except Exception as e:
    print(f"Error: {e}")
