"""
Test script to verify status behavior and colors in Technician Dashboard
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission, Device

print("=" * 70)
print("TESTING STATUS BEHAVIOR FOR TECHNICIAN DASHBOARD")
print("=" * 70)

# Get all submissions
submissions = Submission.objects.all().select_related('device')

if not submissions:
    print("\n❌ No submissions found")
else:
    print(f"\n📊 Found {submissions.count()} submission(s):\n")
    
    status_colors = {
        'Active': '🟢 GREEN',
        'Pending': '🟠 ORANGE',
        'Approved': '🔵 BLUE',
        'Rejected': '🔴 RED'
    }
    
    for sub in submissions:
        print(f"Device: {sub.device.interaction_id}")
        print(f"   Status: {sub.status}")
        print(f"   Color: {status_colors.get(sub.status, '⚪ UNKNOWN')}")
        if sub.status == 'Rejected' and sub.remarks:
            print(f"   Rejection Reason: {sub.remarks}")
        print()

print("=" * 70)
print("\n📋 STATUS COLOR MAPPING:")
print("=" * 70)
print("   🟢 Active    → GREEN   (bg-green-100 text-green-800)")
print("   🟠 Pending   → ORANGE  (bg-orange-100 text-orange-800)")
print("   🔵 Approved  → BLUE    (bg-blue-100 text-blue-800)")
print("   🔴 Rejected  → RED     (bg-red-100 text-red-800)")
print("=" * 70)

print("\n✅ EXPECTED BEHAVIOR:")
print("   1. Initially: Status = Active (GREEN)")
print("   2. After submission: Status = Pending (ORANGE)")
print("   3. After approval: Status = Approved (BLUE)")
print("   4. After rejection: Status = Rejected (RED) + Show remarks")
print("=" * 70)

# Check if we have examples of each status
statuses = {}
for sub in submissions:
    if sub.status not in statuses:
        statuses[sub.status] = sub

print("\n📊 CURRENT STATUS EXAMPLES:")
print("=" * 70)
for status, sub in statuses.items():
    print(f"   {status_colors.get(status, '⚪')}: Device {sub.device.interaction_id}")
print("=" * 70)
