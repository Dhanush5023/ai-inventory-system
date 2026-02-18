import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_register():
    print("--- Registration Diagnostics ---")
    # Test 1: Valid registration (already done, but suffix handles it)
    unique_suffix = int(time.time())
    payload = {
        "email": f"testuser_{unique_suffix}@example.com",
        "username": f"user_{unique_suffix}",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "customer"
    }
    
    try:
        print(f"1. Valid Registration Attempt...")
        res = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
        print(f"Status: {res.status_code}")
        
        # Test 2: Short username (validation error)
        print("\n2. Short Username Attempt (should fail 422)...")
        payload["username"] = "ab"
        res = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
        print(f"Status: {res.status_code}")
        print(f"Detail: {res.text}")

        # Test 3: Duplicate Email (should fail 400)
        print("\n3. Duplicate Email Attempt (should fail 400)...")
        payload["username"] = f"user_new_{unique_suffix}"
        payload["email"] = f"testuser_{unique_suffix}@example.com" # Same as Test 1
        res = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
        print(f"Status: {res.status_code}")
        print(f"Detail: {res.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_register()
