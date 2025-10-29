"""
Test script to verify supervisor dashboard-stats endpoint
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission, User
from django.test.client import Client
from django.contrib.auth import get_user_model
import json

print("=" * 70)
print("TESTING SUPERVISOR DASHBOARD STATS ENDPOINT")
print("=" * 70)

# Get or create a supervisor user
User = get_user_model()
supervisor = User.objects.filter(role='supervisor').first()

if not supervisor:
    print("\n❌ No supervisor user found in database")
    print("   Please create a supervisor user first")
    exit(1)

print(f"\n✅ Found supervisor: {supervisor.username}")

# Get actual statistics from database
total_submissions = Submission.objects.count()
pending_submissions = Submission.objects.filter(status='Pending').count()
approved_submissions = Submission.objects.filter(status='Approved').count()
rejected_submissions = Submission.objects.filter(status='Rejected').count()

print(f"\n📊 Database Statistics:")
print(f"   Total Submissions: {total_submissions}")
print(f"   Pending: {pending_submissions}")
print(f"   Approved: {approved_submissions}")
print(f"   Rejected: {rejected_submissions}")

# Create a client and login
client = Client()

# Get JWT token for supervisor
from rest_framework_simplejwt.tokens import RefreshToken
refresh = RefreshToken.for_user(supervisor)
access_token = str(refresh.access_token)

print(f"\n🔑 Generated JWT token for supervisor")

# Test the endpoint
print(f"\n🔄 Testing GET /api/supervisor/dashboard-stats")

response = client.get(
    '/api/supervisor/dashboard-stats',
    HTTP_AUTHORIZATION=f'Bearer {access_token}'
)

print(f"\n📡 Response Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ SUCCESS! Dashboard stats retrieved:")
    print(f"   Total Submissions: {data.get('total_submissions')}")
    print(f"   Pending: {data.get('pending_submissions')}")
    print(f"   Approved: {data.get('approved_submissions')}")
    print(f"   Rejected: {data.get('rejected_submissions')}")
    
    # Verify data matches
    if (data.get('total_submissions') == total_submissions and
        data.get('pending_submissions') == pending_submissions and
        data.get('approved_submissions') == approved_submissions and
        data.get('rejected_submissions') == rejected_submissions):
        print(f"\n✅ Data verification PASSED - All counts match!")
    else:
        print(f"\n⚠️  Data mismatch detected")
else:
    print(f"\n❌ FAILED! Error response:")
    try:
        error_data = response.json()
        print(f"   {json.dumps(error_data, indent=2)}")
    except:
        print(f"   {response.content}")

print("\n" + "=" * 70)
