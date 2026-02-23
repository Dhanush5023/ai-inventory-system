import requests

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "email": "admin@inventory.com",
        "password": "admin123"
    }
    
    try:
        print(f"Testing login at {url}...")
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 200:
            print("LOGIN TEST PASSED")
            token = response.json().get("access_token")
            # Test /me endpoint
            me_url = "http://localhost:8000/api/v1/auth/me"
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(me_url, headers=headers)
            print(f"Me Status Code: {me_response.status_code}")
            print(f"Me Response Body: {me_response.json()}")
        else:
            print("LOGIN TEST FAILED")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
