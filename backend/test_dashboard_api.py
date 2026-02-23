import requests

r = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={"email": "admin@inventory.com", "password": "admin123"})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test analytics
a = requests.get('http://127.0.0.1:8000/api/v1/analytics', headers=headers)
data = a.json()
print("=== ANALYTICS ===")
for kpi in data.get('overview', {}).get('kpis', []):
    print(f"  KPI: {kpi['label']} = {kpi['value']}")
print(f"  Sales by day points: {len(data.get('sales_metrics', {}).get('sales_by_day', []))}")

# Test market intelligence
m = requests.get('http://127.0.0.1:8000/api/v1/analytics/market-intelligence', headers=headers)
mi = m.json()
print("\n=== MARKET INTELLIGENCE ===")
print(f"  ROI Score: {mi['brief']['roi_score']}")
print(f"  Headline: {mi['brief']['headline_insight'][:80]}")
print(f"  Summary: {mi['brief']['summary'][:80]}")
for ins in mi.get('insights', []):
    print(f"  Insight [{ins['impact_level']}]: {ins['title']} - {ins['description'][:60]}")
