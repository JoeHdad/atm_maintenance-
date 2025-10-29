"""
Feature 2.1 Test: Create Technician Account (Backend)
Tests the POST /api/host/technicians/ endpoint
"""

import os
import django
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from django.test import Client
from core.models import User

print("=" * 80)
print("FEATURE 2.1 TEST: CREATE TECHNICIAN ACCOUNT (BACKEND)")
print("=" * 80)

client = Client()

# Test 1: Login as Data Host
print("\n[TEST 1] Login as Data Host...")
try:
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'host', 'password': 'host123'}),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access')
        print(f"[PASS] Login successful")
        print(f"   Access token: {access_token[:50]}...")
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Error: {e}")
    exit(1)

# Test 2: Create technician with valid data
print("\n[TEST 2] Create technician with valid data...")
try:
    technician_data = {
        'username': 'tech_test1',
        'password': 'SecurePass123!',
        'city': 'Riyadh'
    }
    
    response = client.post(
        '/api/host/technicians/',
        data=json.dumps(technician_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 201:
        print(f"[PASS] Technician created successfully")
        print(f"   ID: {data.get('id')}")
        print(f"   Username: {data.get('username')}")
        print(f"   Role: {data.get('role')}")
        print(f"   City: {data.get('city')}")
        
        # Verify password is not in response
        if 'password' not in data:
            print(f"[PASS] Password excluded from response")
        else:
            print(f"[FAIL] WARNING: Password exposed in response!")
    else:
        print(f"[FAIL] Failed to create technician")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 3: Try to create technician with duplicate username
print("\n[TEST 3] Try to create technician with duplicate username...")
try:
    duplicate_data = {
        'username': 'tech_test1',  # Same as above
        'password': 'AnotherPass123!',
        'city': 'Jeddah'
    }
    
    response = client.post(
        '/api/host/technicians/',
        data=json.dumps(duplicate_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        print(f"[PASS] Duplicate username rejected (expected)")
        print(f"   Error: {data}")
    else:
        print(f"[FAIL] Should have rejected duplicate username")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 4: Try with weak password
print("\n[TEST 4] Try to create technician with weak password...")
try:
    weak_pass_data = {
        'username': 'tech_test2',
        'password': '123',  # Too short
        'city': 'Dammam'
    }
    
    response = client.post(
        '/api/host/technicians/',
        data=json.dumps(weak_pass_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        print(f"[PASS] Weak password rejected (expected)")
        print(f"   Error: {data}")
    else:
        print(f"[FAIL] Should have rejected weak password")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 5: Try with non-alphanumeric username
print("\n[TEST 5] Try to create technician with non-alphanumeric username...")
try:
    invalid_username_data = {
        'username': 'tech@test',  # Contains special character
        'password': 'SecurePass123!',
        'city': 'Mecca'
    }
    
    response = client.post(
        '/api/host/technicians/',
        data=json.dumps(invalid_username_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        print(f"[PASS] Non-alphanumeric username rejected (expected)")
        print(f"   Error: {data}")
    else:
        print(f"[FAIL] Should have rejected non-alphanumeric username")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 6: Try without authentication
print("\n[TEST 6] Try to create technician without authentication...")
try:
    response = client.post(
        '/api/host/technicians/',
        data=json.dumps({
            'username': 'tech_test4',
            'password': 'SecurePass123!',
            'city': 'Medina'
        }),
        content_type='application/json'
        # No Authorization header
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 401:
        print(f"[PASS] Unauthenticated request rejected (expected)")
    else:
        print(f"[FAIL] Should have rejected unauthenticated request")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 7: Try with technician role (not host)
print("\n[TEST 7] Try to create technician as technician (not host)...")
try:
    # Login as technician
    tech_response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'technician1', 'password': 'tech123'}),
        content_type='application/json'
    )
    
    if tech_response.status_code == 200:
        tech_token = tech_response.json().get('access')
        
        response = client.post(
            '/api/host/technicians/',
            data=json.dumps({
                'username': 'tech_test5',
                'password': 'SecurePass123!',
                'city': 'Tabuk'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {tech_token}'
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 403:
            print(f"[PASS] Non-host user rejected (expected)")
        else:
            print(f"[FAIL] Should have rejected non-host user")
    else:
        print(f"[FAIL] Could not login as technician")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 8: Verify created technician in database
print("\n[TEST 8] Verify created technician in database...")
try:
    technician = User.objects.filter(username='tech_test1').first()
    
    if technician:
        print(f"[PASS] Technician found in database")
        print(f"   Username: {technician.username}")
        print(f"   Role: {technician.role}")
        print(f"   City: {technician.city}")
        print(f"   Is Active: {technician.is_active}")
        
        # Verify password is hashed
        if technician.password.startswith('pbkdf2_sha256'):
            print(f"[PASS] Password is properly hashed")
        else:
            print(f"[FAIL] Password not properly hashed!")
        
        # Verify role is technician
        if technician.role == 'technician':
            print(f"[PASS] Role correctly set to 'technician'")
        else:
            print(f"[FAIL] Role not set correctly!")
    else:
        print(f"[FAIL] Technician not found in database")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# Test 9: Test login with created technician
print("\n[TEST 9] Test login with created technician...")
try:
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'tech_test1', 'password': 'SecurePass123!'}),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[PASS] Created technician can login")
        print(f"   User: {data.get('user', {}).get('username')}")
        print(f"   Role: {data.get('user', {}).get('role')}")
    else:
        print(f"[FAIL] Created technician cannot login")
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

print("\n" + "=" * 80)
print("FEATURE 2.1 TEST COMPLETE")
print("=" * 80)

# Cleanup: Delete test technician
print("\n[CLEANUP] Removing test technician...")
try:
    User.objects.filter(username='tech_test1').delete()
    print("[PASS] Test data cleaned up")
except Exception as e:
    print(f"[WARN] Cleanup warning: {e}")
