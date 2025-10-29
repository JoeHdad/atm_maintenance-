"""
Comprehensive Test Suite for Option B Implementation
Tests: Unit, Integration, API, Permissions, Edge Cases, Performance
"""

import requests
import json
import os
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
HOST_USERNAME = "test_host"
HOST_PASSWORD = "testpass123"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
    def add_pass(self, test_name, details=""):
        self.passed.append({"test": test_name, "details": details})
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name, error):
        self.failed.append({"test": test_name, "error": str(error)})
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def add_warning(self, test_name, message):
        self.warnings.append({"test": test_name, "message": message})
        print(f"⚠️  WARN: {test_name}")
        print(f"   {message}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"Success Rate: {(len(self.passed)/total*100):.1f}%" if total > 0 else "N/A")
        return len(self.failed) == 0

results = TestResults()

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

# ============================================================================
# UNIT TESTS - Database & Models
# ============================================================================

def test_database_schema():
    """Test 1.1: Verify ExcelUpload table exists"""
    print_header("UNIT TESTS - Database Schema")
    
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='excel_upload'")
        result = cursor.fetchone()
        
        if result:
            results.add_pass("Database: ExcelUpload table exists")
        else:
            results.add_fail("Database: ExcelUpload table missing", "Table not found in database")
            
        # Check columns
        cursor.execute("PRAGMA table_info(excel_upload)")
        columns = cursor.fetchall()
        expected_columns = ['id', 'technician_id', 'uploaded_by_id', 'file_name', 'file_path', 
                          'device_type', 'parsed_data', 'row_count', 'upload_date']
        
        column_names = [col[1] for col in columns]
        missing = [col for col in expected_columns if col not in column_names]
        
        if not missing:
            results.add_pass("Database: All required columns present", f"Found {len(column_names)} columns")
        else:
            results.add_fail("Database: Missing columns", f"Missing: {missing}")
            
    except Exception as e:
        results.add_fail("Database: Schema verification", str(e))

def test_model_relationships():
    """Test 1.2: Verify model relationships"""
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
        django.setup()
        
        from core.models import ExcelUpload, User
        
        # Check if model is importable
        results.add_pass("Model: ExcelUpload model importable")
        
        # Check relationships
        tech_field = ExcelUpload._meta.get_field('technician')
        upload_field = ExcelUpload._meta.get_field('uploaded_by')
        
        if tech_field.related_model == User:
            results.add_pass("Model: Technician relationship correct")
        else:
            results.add_fail("Model: Technician relationship", "Wrong related model")
            
        if upload_field.related_model == User:
            results.add_pass("Model: Uploaded_by relationship correct")
        else:
            results.add_fail("Model: Uploaded_by relationship", "Wrong related model")
            
    except Exception as e:
        results.add_fail("Model: Relationship verification", str(e))

# ============================================================================
# API TESTS - Authentication & Endpoints
# ============================================================================

def test_host_login():
    """Test 2.1: Host login authentication"""
    print_header("API TESTS - Authentication")
    
    try:
        url = f"{BASE_URL}/auth/login/"
        payload = {"username": HOST_USERNAME, "password": HOST_PASSWORD}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'access' in data and 'user' in data:
                if data['user']['role'] == 'host':
                    results.add_pass("API: Host login successful", f"Token received, role: {data['user']['role']}")
                    return data['access']
                else:
                    results.add_fail("API: Host login", f"Wrong role: {data['user']['role']}")
            else:
                results.add_fail("API: Host login", "Missing access token or user data")
        else:
            results.add_fail("API: Host login", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.add_fail("API: Host login", str(e))
    
    return None

def test_create_technician(token):
    """Test 2.2: Create technician endpoint"""
    try:
        url = f"{BASE_URL}/host/technicians/"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create unique username
        timestamp = int(time.time())
        username = f"test_tech_{timestamp}"
        
        payload = {
            "username": username,
            "password": "testpass123",
            "city": "Riyadh"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            results.add_pass("API: Create technician", f"Created: {data['username']} (ID: {data['id']})")
            return data['id'], username
        else:
            results.add_fail("API: Create technician", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.add_fail("API: Create technician", str(e))
    
    return None, None

def test_upload_excel(token, technician_id):
    """Test 2.3: Upload Excel file endpoint"""
    try:
        excel_path = os.path.join(os.path.dirname(__file__), '..', 'test_devices.xlsx')
        
        if not os.path.exists(excel_path):
            results.add_fail("API: Upload Excel", "test_devices.xlsx not found")
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
            results.add_pass("API: Upload Excel", f"Upload ID: {result['upload_id']}, Rows: {result['total_rows']}")
            return result['upload_id']
        else:
            results.add_fail("API: Upload Excel", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.add_fail("API: Upload Excel", str(e))
    
    return None

def test_technician_login(username):
    """Test 2.4: Technician login"""
    try:
        url = f"{BASE_URL}/auth/login/"
        payload = {"username": username, "password": "testpass123"}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data['user']['role'] == 'technician':
                results.add_pass("API: Technician login", f"User: {data['user']['username']}, Role: {data['user']['role']}")
                return data['access']
            else:
                results.add_fail("API: Technician login", f"Wrong role: {data['user']['role']}")
        else:
            results.add_fail("API: Technician login", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("API: Technician login", str(e))
    
    return None

def test_get_excel_data(token):
    """Test 2.5: Get technician Excel data"""
    try:
        url = f"{BASE_URL}/technician/my-excel-data"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data['total_uploads'] > 0:
                upload = data['uploads'][0]
                results.add_pass("API: Get Excel data", 
                               f"Uploads: {data['total_uploads']}, Rows: {upload['row_count']}")
                return data
            else:
                results.add_fail("API: Get Excel data", "No uploads found")
        else:
            results.add_fail("API: Get Excel data", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("API: Get Excel data", str(e))
    
    return None

# ============================================================================
# PERMISSION TESTS
# ============================================================================

def test_permissions(host_token, tech_token):
    """Test 3: Permission and access control"""
    print_header("PERMISSION TESTS")
    
    # Test 3.1: Technician cannot create technicians
    try:
        url = f"{BASE_URL}/host/technicians/"
        headers = {"Authorization": f"Bearer {tech_token}"}
        payload = {"username": "should_fail", "password": "test", "city": "Test"}
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 403:
            results.add_pass("Permission: Technician blocked from creating technicians")
        else:
            results.add_fail("Permission: Technician create block", 
                           f"Expected 403, got {response.status_code}")
    except Exception as e:
        results.add_fail("Permission: Technician create block", str(e))
    
    # Test 3.2: Technician cannot upload Excel
    try:
        url = f"{BASE_URL}/host/upload-excel"
        headers = {"Authorization": f"Bearer {tech_token}"}
        response = requests.post(url, headers=headers)
        
        if response.status_code == 403:
            results.add_pass("Permission: Technician blocked from uploading Excel")
        else:
            results.add_fail("Permission: Technician upload block", 
                           f"Expected 403, got {response.status_code}")
    except Exception as e:
        results.add_fail("Permission: Technician upload block", str(e))
    
    # Test 3.3: Host cannot access technician data endpoint
    try:
        url = f"{BASE_URL}/technician/my-excel-data"
        headers = {"Authorization": f"Bearer {host_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403:
            results.add_pass("Permission: Host blocked from technician endpoint")
        else:
            results.add_fail("Permission: Host endpoint block", 
                           f"Expected 403, got {response.status_code}")
    except Exception as e:
        results.add_fail("Permission: Host endpoint block", str(e))

# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_edge_cases(host_token):
    """Test 4: Edge cases and error handling"""
    print_header("EDGE CASE TESTS")
    
    # Test 4.1: Upload without technician_id
    try:
        url = f"{BASE_URL}/host/upload-excel"
        headers = {"Authorization": f"Bearer {host_token}"}
        response = requests.post(url, headers=headers)
        
        if response.status_code == 400:
            results.add_pass("Edge Case: Upload without technician_id rejected")
        else:
            results.add_fail("Edge Case: Upload validation", 
                           f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_fail("Edge Case: Upload validation", str(e))
    
    # Test 4.2: Upload with invalid technician_id
    try:
        url = f"{BASE_URL}/host/upload-excel"
        headers = {"Authorization": f"Bearer {host_token}"}
        data = {'technician_id': 99999}
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code in [400, 404]:
            results.add_pass("Edge Case: Invalid technician_id rejected")
        else:
            results.add_fail("Edge Case: Invalid technician validation", 
                           f"Expected 400/404, got {response.status_code}")
    except Exception as e:
        results.add_fail("Edge Case: Invalid technician validation", str(e))
    
    # Test 4.3: Login with wrong credentials
    try:
        url = f"{BASE_URL}/auth/login/"
        payload = {"username": "wrong_user", "password": "wrong_pass"}
        response = requests.post(url, json=payload)
        
        if response.status_code in [400, 401]:
            results.add_pass("Edge Case: Wrong credentials rejected", f"Status: {response.status_code}")
        else:
            results.add_fail("Edge Case: Wrong credentials", 
                           f"Expected 400/401, got {response.status_code}")
    except Exception as e:
        results.add_fail("Edge Case: Wrong credentials", str(e))

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_performance(host_token, technician_id):
    """Test 5: Performance benchmarks"""
    print_header("PERFORMANCE TESTS")
    
    # Test 5.1: Upload response time
    try:
        excel_path = os.path.join(os.path.dirname(__file__), '..', 'test_devices.xlsx')
        if os.path.exists(excel_path):
            url = f"{BASE_URL}/host/upload-excel"
            headers = {"Authorization": f"Bearer {host_token}"}
            
            start_time = time.time()
            with open(excel_path, 'rb') as f:
                files = {'file': ('test_devices.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                data = {'technician_id': technician_id, 'device_type': 'Cleaning'}
                response = requests.post(url, files=files, data=data, headers=headers)
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 201:
                if duration < 2000:  # Less than 2 seconds
                    results.add_pass("Performance: Upload speed", f"{duration:.0f}ms (Good)")
                elif duration < 5000:
                    results.add_warning("Performance: Upload speed", f"{duration:.0f}ms (Acceptable)")
                else:
                    results.add_warning("Performance: Upload speed", f"{duration:.0f}ms (Slow)")
            else:
                results.add_fail("Performance: Upload test", f"Upload failed: {response.status_code}")
    except Exception as e:
        results.add_fail("Performance: Upload test", str(e))

# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

def test_data_integrity(excel_data):
    """Test 6: Data integrity and accuracy"""
    print_header("DATA INTEGRITY TESTS")
    
    try:
        if excel_data and excel_data['uploads']:
            upload = excel_data['uploads'][0]
            parsed_data = upload['parsed_data']
            
            # Test 6.1: Data structure
            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                results.add_pass("Data Integrity: Parsed data is valid list", 
                               f"{len(parsed_data)} rows")
            else:
                results.add_fail("Data Integrity: Data structure", "Invalid data structure")
            
            # Test 6.2: Column consistency
            if len(parsed_data) > 1:
                first_row_keys = set(parsed_data[0].keys())
                all_consistent = all(set(row.keys()) == first_row_keys for row in parsed_data)
                
                if all_consistent:
                    results.add_pass("Data Integrity: Column consistency", 
                                   f"{len(first_row_keys)} columns across all rows")
                else:
                    results.add_fail("Data Integrity: Column consistency", 
                                   "Inconsistent columns across rows")
            
            # Test 6.3: Row count accuracy
            if upload['row_count'] == len(parsed_data):
                results.add_pass("Data Integrity: Row count accurate", 
                               f"Reported: {upload['row_count']}, Actual: {len(parsed_data)}")
            else:
                results.add_fail("Data Integrity: Row count", 
                               f"Mismatch - Reported: {upload['row_count']}, Actual: {len(parsed_data)}")
        else:
            results.add_fail("Data Integrity: No data to test", "No uploads found")
            
    except Exception as e:
        results.add_fail("Data Integrity: Tests", str(e))

# ============================================================================
# FILE SYSTEM TESTS
# ============================================================================

def test_file_system():
    """Test 7: File system and storage"""
    print_header("FILE SYSTEM TESTS")
    
    try:
        upload_dir = 'media/excel_uploads'
        
        # Test 7.1: Directory exists
        if os.path.exists(upload_dir):
            results.add_pass("File System: Upload directory exists", upload_dir)
        else:
            results.add_fail("File System: Upload directory", "Directory not found")
            return
        
        # Test 7.2: Files exist
        files = os.listdir(upload_dir)
        if files:
            results.add_pass("File System: Files stored", f"{len(files)} file(s) found")
            
            # Test 7.3: File integrity
            for filename in files:
                filepath = os.path.join(upload_dir, filename)
                size = os.path.getsize(filepath)
                if size > 0:
                    results.add_pass("File System: File integrity", f"{filename} ({size} bytes)")
                else:
                    results.add_fail("File System: File integrity", f"{filename} is empty")
        else:
            results.add_warning("File System: No files", "Upload directory is empty")
            
    except Exception as e:
        results.add_fail("File System: Tests", str(e))

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_all_tests():
    """Execute all test suites"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE TEST SUITE - OPTION B IMPLEMENTATION")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    # Phase 1: Unit Tests
    test_database_schema()
    test_model_relationships()
    
    # Phase 2: API Tests
    host_token = test_host_login()
    if not host_token:
        print("\n❌ Cannot continue without host token")
        results.summary()
        return False
    
    technician_id, tech_username = test_create_technician(host_token)
    if not technician_id:
        print("\n❌ Cannot continue without technician")
        results.summary()
        return False
    
    upload_id = test_upload_excel(host_token, technician_id)
    
    tech_token = test_technician_login(tech_username)
    if not tech_token:
        print("\n❌ Cannot continue without technician token")
        results.summary()
        return False
    
    excel_data = test_get_excel_data(tech_token)
    
    # Phase 3: Permission Tests
    test_permissions(host_token, tech_token)
    
    # Phase 4: Edge Cases
    test_edge_cases(host_token)
    
    # Phase 5: Performance
    test_performance(host_token, technician_id)
    
    # Phase 6: Data Integrity
    test_data_integrity(excel_data)
    
    # Phase 7: File System
    test_file_system()
    
    # Summary
    success = results.summary()
    
    return success

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
