import requests
import sys

base_url = "http://127.0.0.1:8000/api/v1"

# 1. Register
print("Registering test user...")
reg_data = {
    "email": "test_admin_99@example.com",
    "username": "test_admin_99",
    "password": "password123",
    "full_name": "Test Admin",
    "role": "admin"
}
try:
    res = requests.post(f"{base_url}/auth/register", json=reg_data)
    print(f"Register: {res.status_code}")
except Exception:
    pass # Might already exist

# 2. Login
print("Logging in...")
login_data = {
    "email": "test_admin_99@example.com",
    "password": "password123"
}
res = requests.post(f"{base_url}/auth/login", json=login_data)
if res.status_code != 200:
    print(f"Login failed: {res.text}")
    sys.exit(1)

token = res.json()["access_token"]
print("Got token.")

# 2.5 Call Test Endpoint
test_url = f"{base_url}/ai/autonomous/test"
print(f"Calling {test_url}...")
try:
    test_res = requests.get(test_url)
    print(f"Test Status: {test_res.status_code}")
    print(f"Test Response: {test_res.text}")
except Exception as e:
    print(f"Test Request failed: {e}")

# 3. Call Restock
url = f"{base_url}/ai/autonomous/restock/generate"
params = {"auto_receive": "true"}
headers = {"Authorization": f"Bearer {token}"}

print(f"Sending POST to {url} with params {params}...")
try:
    response = requests.post(url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
