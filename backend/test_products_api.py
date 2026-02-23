import requests

# Step 1: Login to get token
login_resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={
    "email": "admin@inventory.com",
    "password": "admin123"
})
print(f"Login status: {login_resp.status_code}")
if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.text}")
    exit()

token = login_resp.json().get('access_token')
print(f"Token obtained: {token[:30]}...")

# Step 2: Fetch products
products_resp = requests.get(
    'http://127.0.0.1:8000/api/v1/products?limit=5',
    headers={'Authorization': f'Bearer {token}'}
)
print(f"\nProducts status: {products_resp.status_code}")
data = products_resp.json()
print(f"Total products: {data.get('total')}")
print(f"Keys in response: {list(data.keys())}")
products = data.get('products', [])
print(f"Products returned: {len(products)}")
if products:
    print("First product:", {k: v for k, v in list(products[0].items())[:5]})
else:
    print("ERROR: Empty products list!")
    print("Raw response:", products_resp.text[:500])
