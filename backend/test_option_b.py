"""
Test script for Option B implementation
Tests the complete flow: Create technician → Upload Excel → Fetch data
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
HOST_USERNAME = "test_host"
HOST_PASSWORD = "testpass123"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def login_as_host():
    """Login as Data Host"""
    print_section("1. LOGIN AS DATA HOST")
    
    url = f"{BASE_URL}/auth/login/"
    payload = {"username": HOST_USERNAME, "password": HOST_PASSWORD}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful: {data['user']['username']} ({data['user']['role']})")
        return data['access']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def create_technician(token):
    """Create a test technician"""
    print_section("2. CREATE TEST TECHNICIAN")
    
    url = f"{BASE_URL}/host/technicians/"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "username": "test_tech_option_b",
        "password": "testpass123",
        "city": "Riyadh"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Technician created: {data['username']} (ID: {data['id']})")
        return data['id']
    elif response.status_code == 400 and 'username' in response.json():
        print(f"ℹ️  Technician already exists, fetching ID...")
        # Get existing technician
        response = requests.get(f"{BASE_URL}/host/technicians/", headers=headers)
        if response.status_code == 200:
            techs = response.json()
            for tech in techs:
                if tech['username'] == 'test_tech_option_b':
                    print(f"✅ Found existing technician: {tech['username']} (ID: {tech['id']})")
                    return tech['id']
        print(f"❌ Could not find or create technician")
        return None
    else:
        print(f"❌ Failed to create technician: {response.text}")
        return None

def upload_excel(token, technician_id):
    """Upload a test Excel file"""
    print_section("3. UPLOAD EXCEL FILE")
    
    # Check if test Excel file exists
    excel_path = os.path.join(os.path.dirname(__file__), '..', 'test_devices.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"❌ Test Excel file not found: {excel_path}")
        print(f"ℹ️  Please ensure test_devices.xlsx exists in the project root")
        return None
    
    url = f"{BASE_URL}/host/upload-excel"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(excel_path, 'rb') as f:
        files = {'file': ('test_devices.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        data = {
            'technician_id': technician_id,
            'device_type': 'Cleaning'
        }
        
        response = requests.post(url, files=files, data=data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Excel uploaded successfully!")
        print(f"   - Upload ID: {result['upload_id']}")
        print(f"   - File: {result['file_name']}")
        print(f"   - Rows: {result['total_rows']}")
        print(f"   - Technician: {result['technician']['username']}")
        return result['upload_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def login_as_technician():
    """Login as the created technician"""
    print_section("4. LOGIN AS TECHNICIAN")
    
    url = f"{BASE_URL}/auth/login/"
    payload = {
        "username": "test_tech_option_b",
        "password": "testpass123"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Technician login successful: {data['user']['username']}")
        print(f"   - Role: {data['user']['role']}")
        print(f"   - City: {data['user']['city']}")
        return data['access']
    else:
        print(f"❌ Technician login failed: {response.text}")
        return None

def fetch_technician_data(token):
    """Fetch Excel data as technician"""
    print_section("5. FETCH TECHNICIAN EXCEL DATA")
    
    url = f"{BASE_URL}/technician/my-excel-data"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Data fetched successfully!")
        print(f"   - Technician: {data['technician']['username']}")
        print(f"   - Total Uploads: {data['total_uploads']}")
        
        if data['uploads']:
            for upload in data['uploads']:
                print(f"\n   📄 Upload: {upload['file_name']}")
                print(f"      - Rows: {upload['row_count']}")
                print(f"      - Device Type: {upload['device_type']}")
                print(f"      - Uploaded By: {upload['uploaded_by']}")
                
                if upload['parsed_data']:
                    print(f"      - Data Preview (first 3 rows):")
                    for i, row in enumerate(upload['parsed_data'][:3]):
                        print(f"        Row {i+1}: {row}")
        
        return True
    else:
        print(f"❌ Failed to fetch data: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  OPTION B IMPLEMENTATION TEST")
    print("  Testing: Create → Upload → Login → View")
    print("="*70)
    
    # Test 1: Login as Host
    host_token = login_as_host()
    if not host_token:
        print("\n❌ Test failed at login")
        return
    
    # Test 2: Create Technician
    technician_id = create_technician(host_token)
    if not technician_id:
        print("\n❌ Test failed at technician creation")
        return
    
    # Test 3: Upload Excel
    upload_id = upload_excel(host_token, technician_id)
    if not upload_id:
        print("\n❌ Test failed at Excel upload")
        return
    
    # Test 4: Login as Technician
    tech_token = login_as_technician()
    if not tech_token:
        print("\n❌ Test failed at technician login")
        return
    
    # Test 5: Fetch Data as Technician
    success = fetch_technician_data(tech_token)
    
    # Summary
    print_section("TEST SUMMARY")
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\nOption B implementation is working correctly:")
        print("  ✅ Host can create technicians")
        print("  ✅ Host can upload Excel files")
        print("  ✅ Files are stored and linked to technicians")
        print("  ✅ Technicians can log in")
        print("  ✅ Technicians can view their Excel data")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
