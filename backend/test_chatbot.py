import requests
import json

def test_chatbot():
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    login_data = {
        "email": "admin@inventory.com",
        "password": "admin123"
    }
    
    print("--- Testing Login ---")
    login_res = requests.post(login_url, json=login_data)
    if login_res.status_code != 200:
        print(f"FAILED: Login returned {login_res.status_code}")
        return
        
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Testing Chatbot Query ---")
    query_url = "http://127.0.0.1:8000/api/v1/ai/chatbot/query"
    query_data = {"question": "Summarize the revenue"}
    
    try:
        query_res = requests.post(query_url, json=query_data, headers=headers)
        print(f"Status Code: {query_res.status_code}")
        print(f"Response: {json.dumps(query_res.json(), indent=2)}")
        
        if query_res.status_code == 200:
            print("PASSED: Chatbot answered successfully")
        else:
            print("FAILED: Chatbot query failed")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_chatbot()
