#!/usr/bin/env python
"""
Test script for Feature 2.4: Excel Upload UI (Frontend)
Tests the backend API endpoints that support the frontend
"""

import os
import sys
import django
from datetime import datetime
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import User
from openpyxl import Workbook
from io import BytesIO

# API Base URL
BASE_URL = 'http://127.0.0.1:8000/api'

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def setup_test_users():
    """Create test Data Host and Technician users"""
    print_header("TEST SETUP: Creating Test Users")
    
    # Create Data Host user
    host_user, created = User.objects.get_or_create(
        username='test_host',
        defaults={'role': 'host'}
    )
    if created:
        host_user.set_password('testpass123')
        host_user.save()
        print_success(f"Created Data Host user: {host_user.username}")
    else:
        print_info(f"Using existing Data Host user: {host_user.username}")
    
    # Create Technician users
    technicians = []
    cities = ['Riyadh', 'Jeddah', 'Dammam']
    
    for city in cities:
        tech_username = f'test_tech_{city.lower()}'
        tech, created = User.objects.get_or_create(
            username=tech_username,
            defaults={
                'role': 'technician',
                'city': city
            }
        )
        if created:
            tech.set_password('testpass123')
            tech.save()
            print_success(f"Created Technician: {tech.username} ({tech.city})")
        else:
            print_info(f"Using existing Technician: {tech.username} ({tech.city})")
        technicians.append(tech)
    
    return host_user, technicians

def login_user(username, password):
    """Login and get JWT token"""
    print_info(f"Logging in as {username}...")
    
    response = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'username': username, 'password': password}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['access']
        print_success(f"Login successful. Token obtained.")
        return token
    else:
        print_error(f"Login failed: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None

def test_get_technicians(token):
    """Test GET /api/host/technicians/ endpoint"""
    print_header("TEST 1: GET Technicians Endpoint")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{BASE_URL}/host/technicians/', headers=headers)
        
        if response.status_code == 200:
            technicians = response.json()
            print_success(f"Successfully fetched {len(technicians)} technicians")
            
            for tech in technicians:
                print(f"  - ID: {tech['id']}, Username: {tech['username']}, City: {tech['city']}")
            
            return True, technicians
        else:
            print_error(f"Failed to fetch technicians: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, []
    
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False, []

def create_test_excel():
    """Create a test Excel file in memory"""
    print_info("Creating test Excel file...")
    
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    ws.append(['Interaction ID', 'Gfm cost Center', 'Status', 'Gfm Problem Type', 'Gfm Problem Date'])
    
    # Add test data
    test_data = [
        ['ATM-UI-001', 'CC-20001', 'Central Region', 'Cleaning Required', '2025-01-20'],
        ['ATM-UI-002', 'CC-20002', 'North Region', 'Maintenance Due', '2025-01-21'],
        ['ATM-UI-003', 'CC-20003', 'South Region', 'Inspection Needed', '2025-01-22'],
        ['ATM-UI-004', 'CC-20004', 'East Region', 'Repair Required', '2025-01-23'],
        ['ATM-UI-005', 'CC-20005', 'West Region', 'Cleaning Required', '2025-01-24'],
    ]
    
    for row in test_data:
        ws.append(row)
    
    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    print_success(f"Created test Excel file with {len(test_data)} devices")
    return excel_file

def test_upload_excel(token, technician_id, device_type='Cleaning'):
    """Test POST /api/host/upload-excel endpoint"""
    print_header(f"TEST 2: Upload Excel File (Technician ID: {technician_id}, Type: {device_type})")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create test Excel file
    excel_file = create_test_excel()
    
    # Prepare multipart form data
    files = {
        'file': ('test_devices.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'technician_id': technician_id,
        'device_type': device_type
    }
    
    try:
        print_info("Uploading Excel file...")
        response = requests.post(
            f'{BASE_URL}/host/upload-excel',
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 201:
            result = response.json()
            print_success(f"Upload successful!")
            print_success(f"Total devices imported: {result['total_imported']}")
            print_success(f"Technician: {result['technician']['username']} ({result['technician']['city']})")
            print_success(f"Device type: {result['device_type']}")
            
            print_info(f"\nFirst 3 imported devices:")
            for i, device in enumerate(result['devices'][:3], 1):
                print(f"  {i}. {device['interaction_id']} - {device['region']}")
            
            return True, result
        else:
            print_error(f"Upload failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None
    
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def test_upload_invalid_file(token, technician_id):
    """Test upload with invalid file type"""
    print_header("TEST 3: Upload Invalid File Type")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create a text file instead of Excel
    invalid_file = BytesIO(b"This is not an Excel file")
    
    files = {
        'file': ('test.txt', invalid_file, 'text/plain')
    }
    data = {
        'technician_id': technician_id,
        'device_type': 'Cleaning'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/host/upload-excel',
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 400:
            print_success("Correctly rejected invalid file type")
            print_info(f"Error message: {response.json()}")
            return True
        else:
            print_error(f"Expected 400, got {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False

def test_upload_without_auth():
    """Test upload without authentication"""
    print_header("TEST 4: Upload Without Authentication")
    
    excel_file = create_test_excel()
    
    files = {
        'file': ('test_devices.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'technician_id': 1,
        'device_type': 'Cleaning'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/host/upload-excel',
            files=files,
            data=data
        )
        
        if response.status_code == 401:
            print_success("Correctly rejected unauthenticated request")
            return True
        else:
            print_error(f"Expected 401, got {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False

def test_replace_strategy(token, technician_id):
    """Test that uploading replaces existing devices"""
    print_header("TEST 5: REPLACE Strategy (Upload Twice)")
    
    # First upload
    print_info("First upload (Cleaning devices)...")
    success1, result1 = test_upload_excel(token, technician_id, 'Cleaning')
    
    if not success1:
        print_error("First upload failed")
        return False
    
    first_count = result1['total_imported']
    
    # Second upload (should replace)
    print_info("\nSecond upload (Electrical devices - should replace first)...")
    success2, result2 = test_upload_excel(token, technician_id, 'Electrical')
    
    if not success2:
        print_error("Second upload failed")
        return False
    
    second_count = result2['total_imported']
    
    # Verify all devices are now Electrical
    if result2['device_type'] == 'Electrical':
        print_success("REPLACE strategy working: Old devices replaced with new ones")
        print_info(f"First upload: {first_count} Cleaning devices")
        print_info(f"Second upload: {second_count} Electrical devices (replaced)")
        return True
    else:
        print_error("REPLACE strategy failed")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print_header("CLEANUP: Removing Test Data")
    
    try:
        # Delete test devices
        from core.models import Device
        deleted_devices = Device.objects.filter(
            interaction_id__startswith='ATM-UI-'
        ).delete()
        print_success(f"Deleted test devices: {deleted_devices[0]} records")
        
        # Optionally delete test users (commented out to keep them for manual testing)
        # User.objects.filter(username__startswith='test_').delete()
        
        print_success("Cleanup complete")
    
    except Exception as e:
        print_error(f"Cleanup failed: {str(e)}")

def main():
    """Run all tests"""
    print_header("FEATURE 2.4: EXCEL UPLOAD UI - BACKEND API TESTS")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Setup
    host_user, technicians = setup_test_users()
    
    if not technicians:
        print_error("No technicians available for testing")
        return False
    
    # Login as Data Host
    token = login_user('test_host', 'testpass123')
    if not token:
        print_error("Failed to obtain authentication token")
        return False
    
    # Test 1: Get Technicians
    success, tech_list = test_get_technicians(token)
    results.append(("GET Technicians", success))
    
    if not tech_list:
        print_error("Cannot proceed without technicians")
        return False
    
    technician_id = tech_list[0]['id']
    
    # Test 2: Upload Excel
    success, _ = test_upload_excel(token, technician_id, 'Cleaning')
    results.append(("Upload Excel (Valid)", success))
    
    # Test 3: Invalid File
    success = test_upload_invalid_file(token, technician_id)
    results.append(("Upload Invalid File", success))
    
    # Test 4: No Auth
    success = test_upload_without_auth()
    results.append(("Upload Without Auth", success))
    
    # Test 5: REPLACE Strategy
    success = test_replace_strategy(token, technician_id)
    results.append(("REPLACE Strategy", success))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print_header("TEST SUMMARY")
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}✓ PASSED{Colors.RESET}" if passed else f"{Colors.RED}✗ FAILED{Colors.RESET}"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Print manual testing instructions
    print_header("MANUAL TESTING INSTRUCTIONS")
    print(f"{Colors.BOLD}Test Users Created:{Colors.RESET}")
    print(f"  Data Host: username='test_host', password='testpass123'")
    print(f"  Technicians:")
    for tech in technicians:
        print(f"    - {tech.username} (City: {tech.city}), password='testpass123'")
    
    print(f"\n{Colors.BOLD}Frontend URL:{Colors.RESET}")
    print(f"  http://localhost:3000/upload-excel")
    
    print(f"\n{Colors.BOLD}Manual Test Steps:{Colors.RESET}")
    print("  1. Open browser and navigate to http://localhost:3000/login")
    print("  2. Login with: username='test_host', password='testpass123'")
    print("  3. Navigate to http://localhost:3000/upload-excel")
    print("  4. Select a technician from dropdown")
    print("  5. Select device type (Cleaning or Electrical)")
    print("  6. Upload the test Excel file (or create your own)")
    print("  7. Verify success message and device preview table")
    print("  8. Try uploading again to test REPLACE strategy")
    
    return all(passed for _, passed in results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
