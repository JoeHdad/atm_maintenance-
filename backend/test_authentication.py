"""
STAGE 1: Backend Authentication Logic Testing
Tests the authentication flow to verify correct credentials are validated properly.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import User
from core.serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

print("=" * 80)
print("STAGE 1: BACKEND AUTHENTICATION LOGIC VERIFICATION")
print("=" * 80)

# Test 1: Check if test users exist
print("\n[TEST 1] Checking database for test users...")
try:
    users = User.objects.all()
    print(f"✅ Total users in database: {users.count()}")
    for user in users:
        print(f"   - Username: {user.username}, Role: {user.role}, Active: {user.is_active}")
except Exception as e:
    print(f"❌ Error querying users: {e}")

# Test 2: Test Django authenticate() function
print("\n[TEST 2] Testing Django authenticate() function...")
test_credentials = [
    ('admin', 'admin123'),
    ('technician1', 'tech123'),
    ('host', 'host123'),
    ('wronguser', 'wrongpass')
]

for username, password in test_credentials:
    user = authenticate(username=username, password=password)
    if user:
        print(f"✅ authenticate('{username}', '{password}') -> SUCCESS")
        print(f"   User object: {user}")
        print(f"   is_active: {user.is_active}")
        print(f"   Role: {user.role}")
    else:
        print(f"❌ authenticate('{username}', '{password}') -> FAILED (returned None)")

# Test 3: Test password hash verification
print("\n[TEST 3] Testing password hash verification...")
try:
    admin_user = User.objects.get(username='admin')
    print(f"✅ Admin user found: {admin_user.username}")
    print(f"   Password hash: {admin_user.password[:50]}...")
    print(f"   check_password('admin123'): {admin_user.check_password('admin123')}")
    print(f"   check_password('wrongpass'): {admin_user.check_password('wrongpass')}")
except User.DoesNotExist:
    print("❌ Admin user not found in database")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Test LoginSerializer validation
print("\n[TEST 4] Testing LoginSerializer validation...")
test_data = [
    {'username': 'admin', 'password': 'admin123'},
    {'username': 'admin', 'password': 'wrongpass'},
    {'username': 'technician1', 'password': 'tech123'},
]

for data in test_data:
    serializer = LoginSerializer(data=data)
    if serializer.is_valid():
        user = serializer.validated_data.get('user')
        print(f"✅ LoginSerializer valid for {data['username']}")
        print(f"   User: {user.username}, Role: {user.role}")
    else:
        print(f"❌ LoginSerializer invalid for {data['username']}")
        print(f"   Errors: {serializer.errors}")

# Test 5: Test JWT token generation
print("\n[TEST 5] Testing JWT token generation...")
try:
    admin_user = User.objects.get(username='admin')
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    print(f"✅ JWT tokens generated successfully")
    print(f"   Access token length: {len(access_token)} chars")
    print(f"   Refresh token length: {len(refresh_token)} chars")
    print(f"   Access token preview: {access_token[:50]}...")
except Exception as e:
    print(f"❌ Error generating tokens: {e}")

# Test 6: Test is_active flag
print("\n[TEST 6] Testing is_active flag for all users...")
try:
    for user in User.objects.all():
        print(f"   {user.username}: is_active = {user.is_active}")
        if not user.is_active:
            print(f"   ⚠️  WARNING: User '{user.username}' is INACTIVE!")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("STAGE 1 COMPLETE")
print("=" * 80)
