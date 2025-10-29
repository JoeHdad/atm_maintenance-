"""
STAGES 2-6: Comprehensive Testing
Tests frontend-backend communication, error handling, database, and configuration.
"""

import os
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from django.test import Client
from django.urls import resolve, reverse
from core.models import User
from django.core.management import call_command

print("=" * 80)
print("STAGE 2: FRONTEND-BACKEND COMMUNICATION")
print("=" * 80)

# Test 1: Verify URL routing
print("\n[TEST 1] Verifying URL routing...")
try:
    # Test login URL
    login_url = '/api/auth/login/'
    resolved = resolve(login_url)
    print(f"✅ URL '{login_url}' resolves to: {resolved.func.__name__}")
    
    # Test refresh URL
    refresh_url = '/api/auth/refresh/'
    resolved = resolve(refresh_url)
    print(f"✅ URL '{refresh_url}' resolves to: {resolved.func.__name__ if hasattr(resolved.func, '__name__') else resolved.func.__class__.__name__}")
except Exception as e:
    print(f"❌ URL routing error: {e}")

# Test 2: Test API endpoint with Django test client
print("\n[TEST 2] Testing API endpoint with Django test client...")
client = Client()

# Test valid credentials
print("\n  Testing VALID credentials (admin/admin123):")
try:
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json'
    )
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ SUCCESS: Login endpoint working")
        print(f"     Response keys: {list(data.keys())}")
        print(f"     User: {data.get('user', {}).get('username')}")
        print(f"     Role: {data.get('user', {}).get('role')}")
        print(f"     Access token length: {len(data.get('access', ''))}")
    else:
        print(f"  ❌ FAILED: Status {response.status_code}")
        print(f"     Response: {response.content.decode()}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test invalid credentials
print("\n  Testing INVALID credentials (admin/wrongpass):")
try:
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'admin', 'password': 'wrongpass'}),
        content_type='application/json'
    )
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        print(f"  ✅ SUCCESS: Proper error handling")
        print(f"     Error format: {data}")
    else:
        print(f"  ⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("STAGE 3: ERROR HANDLING & RESPONSE PARSING")
print("=" * 80)

# Test 3: Verify error response format
print("\n[TEST 3] Verifying error response format...")
test_cases = [
    {'username': 'admin', 'password': 'wrongpass', 'expected': 400},
    {'username': 'nonexistent', 'password': 'anypass', 'expected': 400},
    {'username': '', 'password': 'anypass', 'expected': 400},
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n  Test Case {i}: username='{test_case['username']}', password='{test_case['password']}'")
    try:
        response = client.post(
            '/api/auth/login/',
            data=json.dumps({'username': test_case['username'], 'password': test_case['password']}),
            content_type='application/json'
        )
        
        if response.status_code == test_case['expected']:
            print(f"  ✅ Status code: {response.status_code} (expected)")
            data = response.json()
            print(f"     Error format: {data}")
            
            # Check if error is in expected format
            if 'non_field_errors' in data:
                print(f"     ✅ DRF error format detected")
                print(f"     Error message: {data['non_field_errors'][0]}")
        else:
            print(f"  ⚠️  Status: {response.status_code} (expected {test_case['expected']})")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("STAGE 4: DATABASE & MIGRATIONS VALIDITY")
print("=" * 80)

# Test 4: Check migrations
print("\n[TEST 4] Checking database migrations...")
try:
    from django.db.migrations.executor import MigrationExecutor
    from django.db import connection
    
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    if not plan:
        print("✅ All migrations are applied")
    else:
        print(f"⚠️  Unapplied migrations found: {len(plan)}")
        for migration, backwards in plan:
            print(f"   - {migration}")
except Exception as e:
    print(f"❌ Error checking migrations: {e}")

# Test 5: Verify database tables
print("\n[TEST 5] Verifying database tables...")
try:
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
    
    table_names = [table[0] for table in tables]
    required_tables = ['user', 'device', 'technician_device', 'submission', 'photo']
    
    print(f"  Total tables: {len(table_names)}")
    for table in required_tables:
        if table in table_names:
            print(f"  ✅ Table '{table}' exists")
        else:
            print(f"  ❌ Table '{table}' MISSING")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Verify user data integrity
print("\n[TEST 6] Verifying user data integrity...")
try:
    users = User.objects.all()
    print(f"  Total users: {users.count()}")
    
    for user in users:
        issues = []
        if not user.username:
            issues.append("missing username")
        if not user.password:
            issues.append("missing password hash")
        if not user.role:
            issues.append("missing role")
        if not user.is_active:
            issues.append("inactive account")
        
        if issues:
            print(f"  ⚠️  User '{user.username}': {', '.join(issues)}")
        else:
            print(f"  ✅ User '{user.username}': all checks passed")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("STAGE 5: FRONTEND STATE MANAGEMENT (Backend Perspective)")
print("=" * 80)

# Test 7: Verify JWT token structure
print("\n[TEST 7] Verifying JWT token structure...")
try:
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access')
        refresh_token = data.get('refresh')
        
        # Check token structure (header.payload.signature)
        if access_token and access_token.count('.') == 2:
            print(f"  ✅ Access token has valid JWT structure")
            
            # Decode payload (not verifying signature, just checking structure)
            import base64
            payload = access_token.split('.')[1]
            # Add padding if needed
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = json.loads(base64.b64decode(payload))
            print(f"     Token payload keys: {list(decoded.keys())}")
            print(f"     User ID: {decoded.get('user_id')}")
            print(f"     Token type: {decoded.get('token_type')}")
        else:
            print(f"  ❌ Invalid token structure")
        
        if refresh_token and refresh_token.count('.') == 2:
            print(f"  ✅ Refresh token has valid JWT structure")
        else:
            print(f"  ❌ Invalid refresh token structure")
    else:
        print(f"  ❌ Could not get tokens (status {response.status_code})")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("STAGE 6: CONFIGURATION & ROUTING")
print("=" * 80)

# Test 8: Check Django settings
print("\n[TEST 8] Checking Django configuration...")
try:
    from django.conf import settings
    
    checks = [
        ('DEBUG', hasattr(settings, 'DEBUG')),
        ('SECRET_KEY', hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY != ''),
        ('ALLOWED_HOSTS', hasattr(settings, 'ALLOWED_HOSTS')),
        ('CORS_ALLOW_ALL_ORIGINS', hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS')),
        ('REST_FRAMEWORK', hasattr(settings, 'REST_FRAMEWORK')),
        ('SIMPLE_JWT', hasattr(settings, 'SIMPLE_JWT')),
    ]
    
    for setting_name, exists in checks:
        if exists:
            print(f"  ✅ {setting_name} configured")
        else:
            print(f"  ❌ {setting_name} MISSING")
    
    # Check CORS settings
    if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'):
        print(f"     CORS_ALLOW_ALL_ORIGINS: {settings.CORS_ALLOW_ALL_ORIGINS}")
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"     CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 9: Test CORS headers
print("\n[TEST 9] Testing CORS headers in response...")
try:
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json',
        HTTP_ORIGIN='http://localhost:3000'
    )
    
    cors_headers = {
        'Access-Control-Allow-Origin': response.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Credentials': response.get('Access-Control-Allow-Credentials'),
    }
    
    print(f"  Response status: {response.status_code}")
    for header, value in cors_headers.items():
        if value:
            print(f"  ✅ {header}: {value}")
        else:
            print(f"  ⚠️  {header}: Not present")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("ALL STAGES COMPLETE")
print("=" * 80)
