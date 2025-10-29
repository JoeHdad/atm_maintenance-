import requests
import json

BASE_URL = "http://localhost:8000/api"

print("=" * 80)
print("API ENDPOINT TESTING - PHASE 4")
print("=" * 80)

# Step 1: Login as supervisor
print("\n🔐 TEST 1: Login as Supervisor")
print("-" * 80)
login_data = {
    "username": "admin",
    "password": "admin123"  # Adjust if different
}

try:
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access')
        user_role = tokens.get('role')
        print(f"✅ Login successful!")
        print(f"   Role: {user_role}")
        print(f"   Token: {access_token[:50]}...")
        
        if user_role != 'supervisor':
            print(f"⚠️  WARNING: User role is '{user_role}', expected 'supervisor'")
    else:
        print(f"❌ Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Headers with token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Step 2: Test GET /api/supervisor/submissions
print("\n\n📋 TEST 2: GET /api/supervisor/submissions (List All)")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/supervisor/submissions", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   Total Submissions: {data.get('count')}")
        
        if data.get('submissions'):
            for sub in data['submissions'][:2]:
                print(f"\n   Submission ID: {sub['id']}")
                print(f"     Device: {sub['device_info']['interaction_id']}")
                print(f"     Technician: {sub['technician_name']}")
                print(f"     Status: {sub['status']}")
                print(f"     Photos: {len(sub['photos'])}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 3: Test GET /api/supervisor/submissions with filters
print("\n\n🔍 TEST 3: GET /api/supervisor/submissions?status=Pending")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/supervisor/submissions?status=Pending", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   Pending Submissions: {data.get('count')}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 4: Test GET /api/supervisor/submissions/<id>
print("\n\n📄 TEST 4: GET /api/supervisor/submissions/1 (Detail)")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/supervisor/submissions/1", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        sub = data.get('submission')
        print(f"✅ Success!")
        print(f"   Submission ID: {sub['id']}")
        print(f"   Device: {sub['device_info']['interaction_id']}")
        print(f"   Status: {sub['status']}")
        print(f"   Photos: {len(sub['photos'])}")
        print(f"   Photos by section:")
        for section in [1, 2, 3]:
            section_photos = [p for p in sub['photos'] if p['section'] == section]
            print(f"     Section {section}: {len(section_photos)} photos")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 5: Test PATCH /api/supervisor/submissions/<id>/approve
print("\n\n✅ TEST 5: PATCH /api/supervisor/submissions/1/approve")
print("-" * 80)
try:
    response = requests.patch(
        f"{BASE_URL}/supervisor/submissions/1/approve",
        headers=headers,
        json={"remarks": "Good work!"}
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   Message: {data.get('message')}")
        print(f"   New Status: {data['submission']['status']}")
        print(f"   PDF Status: {data.get('pdf_status')}")
        print(f"   Email Status: {data.get('email_status')}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 6: Test PATCH /api/supervisor/submissions/<id>/reject
print("\n\n❌ TEST 6: PATCH /api/supervisor/submissions/2/reject")
print("-" * 80)
try:
    response = requests.patch(
        f"{BASE_URL}/supervisor/submissions/2/reject",
        headers=headers,
        json={"remarks": "Photos are unclear, please resubmit with better quality images."}
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   Message: {data.get('message')}")
        print(f"   New Status: {data['submission']['status']}")
        print(f"   Remarks: {data['submission']['remarks']}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 7: Test rejection validation (remarks too short)
print("\n\n⚠️  TEST 7: Reject with short remarks (should fail)")
print("-" * 80)
try:
    # First, reset submission 2 to Pending
    from django.core.management import execute_from_command_line
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
    django.setup()
    from core.models import Submission
    sub = Submission.objects.get(id=2)
    sub.status = 'Pending'
    sub.save()
    print("Reset submission 2 to Pending")
    
    response = requests.patch(
        f"{BASE_URL}/supervisor/submissions/2/reject",
        headers=headers,
        json={"remarks": "Bad"}  # Only 3 characters
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print(f"✅ Validation working! Error: {response.json().get('error')}")
    else:
        print(f"❌ Validation failed - should have rejected short remarks")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 8: Test permission (try with technician token)
print("\n\n🔒 TEST 8: Permission Check (Technician should be denied)")
print("-" * 80)
try:
    # Login as technician
    tech_login = requests.post(f"{BASE_URL}/auth/login/", json={"username": "hary", "password": "hary123"})
    if tech_login.status_code == 200:
        tech_token = tech_login.json().get('access')
        tech_headers = {"Authorization": f"Bearer {tech_token}"}
        
        response = requests.get(f"{BASE_URL}/supervisor/submissions", headers=tech_headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print(f"✅ Permission working! Technician denied access")
        else:
            print(f"❌ Permission failed - technician should be denied")
    else:
        print("⚠️  Could not login as technician to test")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("API TESTING COMPLETE")
print("=" * 80)
