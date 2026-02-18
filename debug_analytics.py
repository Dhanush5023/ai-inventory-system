import requests
import json

def debug_analytics():
    # 1. Login
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {"email": "admin@inventory.com", "password": "admin123"}
    
    try:
        session = requests.Session()
        resp = session.post(login_url, json=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        
        token = resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # 2. Fetch Analytics
        url = "http://localhost:8000/api/v1/analytics"
        print(f"Fetching {url}...")
        resp = session.get(url, headers=headers)
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Response Keys:", data.keys())
            if 'overview' in data:
                print("Overview Keys:", data['overview'].keys())
            if 'sales_metrics' in data:
                print("Sales Metrics Keys:", data['sales_metrics'].keys())
            if 'inventory_metrics' in data:
                print("Inventory Metrics Keys:", data['inventory_metrics'].keys())
        else:
            print(f"Error: {resp.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_analytics()
