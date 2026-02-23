import requests
import json

def get_revenue_summary():
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    login_data = {"email": "admin@inventory.com", "password": "admin123"}
    
    r = requests.post(login_url, json=login_data)
    token = r.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Dashboard Overview
    overview_url = "http://127.0.0.1:8000/api/v1/analytics"
    overview_res = requests.get(overview_url, headers=headers)
    overview_data = overview_res.json()
    
    # 2. Market Intelligence for specific advice
    mi_url = "http://127.0.0.1:8000/api/v1/analytics/market-intelligence"
    mi_res = requests.get(mi_url, headers=headers)
    mi_data = mi_res.json()
    
    summary = {
        "kpis": overview_data.get('overview', {}).get('kpis', []),
        "financials": overview_data.get('financial_metrics', {}),
        "mi_headline": mi_data.get('brief', {}).get('headline_insight', ''),
        "growth": 0
    }
    
    # Clean up Rupee symbol for printing in terminal if needed, but here we just return json
    return summary

if __name__ == "__main__":
    res = get_revenue_summary()
    # Print safe parts
    for kpi in res['kpis']:
        label = kpi['label']
        value = str(kpi['value']).replace('\u20b9', 'INR ')
        print(f"{label}: {value}")
    
    print(f"\nTotal Revenue (Financials): INR {res['financials'].get('total_revenue', 0):,.2f}")
    print(f"Gross Profit: INR {res['financials'].get('gross_profit', 0):,.2f}")
    print(f"Profit Margin: {res['financials'].get('profit_margin', 0)}%")
    print(f"\nMarket Headline: {res['mi_headline']}")
