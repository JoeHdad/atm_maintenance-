import requests

BASE_URL = "http://localhost:8000/api"

# Login as supervisor
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "admin",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get submissions
    response = requests.get(f"{BASE_URL}/supervisor/submissions", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        print("=" * 60)
        print("SUBMISSION DATA STRUCTURE")
        print("=" * 60)
        
        if data.get('submissions'):
            sub = data['submissions'][0]
            print("\nSample Submission:")
            print(f"  ID: {sub['id']}")
            print(f"  Technician Name: {sub['technician_name']}")
            print(f"  Status: {sub['status']}")
            print(f"  Type: {sub['type']}")
            print(f"  Half Month: {sub['half_month']}")
            print(f"  Visit Date: {sub['visit_date']}")
            
            print("\n  Device Info:")
            print(f"    Interaction ID: {sub['device_info']['interaction_id']}")
            print(f"    Cost Center: {sub['device_info']['gfm_cost_center']}")
            print(f"    City: {sub['device_info']['city']}")
            print(f"    Region: {sub['device_info'].get('region', 'N/A')}")
            print(f"    Type: {sub['device_info']['type']}")
            
            print("\n" + "=" * 60)
            print("EXPECTED DISPLAY:")
            print("=" * 60)
            print(f"\n{sub['device_info']['interaction_id']}, {sub['status']}, {sub['technician_name']} • {sub['device_info']['gfm_cost_center']}")
            print(f"Type: {sub['type']} - Half {sub['half_month']}, {sub['device_info']['city']}, {sub['visit_date']}")
    else:
        print(f"Failed: {response.status_code}")
else:
    print(f"Login failed: {login_response.status_code}")
