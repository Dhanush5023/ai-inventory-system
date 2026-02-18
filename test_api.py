import requests
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force SQLite
sys.path.append(os.path.join(os.getcwd(), "backend"))
from backend.app.core.security import create_access_token
from backend.app.core.config import settings

# 1. Generate Token for User 1
print(f"DEBUG: SECRET_KEY = {settings.SECRET_KEY}")
print(f"DEBUG: DATABASE_URL = {settings.DATABASE_URL}")
print("Generating test token...")
token = create_access_token({"sub": 1})
headers = {"Authorization": f"Bearer {token}"}

# 2. Call API
url = "http://127.0.0.1:8000/api/v1/ai/autonomous/restock/generate"
params = {"auto_receive": "true"}

print(f"Sending POST to {url} with params {params}...")
try:
    response = requests.post(url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
