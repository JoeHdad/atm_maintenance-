import requests

try:
    response = requests.get('http://localhost:3000', timeout=2)
    print(f"✅ Frontend server is RUNNING (Status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("❌ Frontend server is NOT RUNNING")
    print("Please start with: npm start (in frontend/atm_frontend directory)")
except Exception as e:
    print(f"⚠️ Error checking frontend: {e}")
