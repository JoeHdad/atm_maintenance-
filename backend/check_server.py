import requests

try:
    response = requests.get('http://127.0.0.1:8000/api/auth/login/', timeout=2)
    print(f"✅ Backend server is RUNNING (Status: {response.status_code})")
except requests.exceptions.ConnectionError:
    print("❌ Backend server is NOT RUNNING")
    print("Please start the server with: python manage.py runserver")
except Exception as e:
    print(f"⚠️ Error checking server: {e}")
