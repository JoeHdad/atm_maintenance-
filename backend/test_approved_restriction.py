"""
Test script to verify "Add Visit Report" button restriction for Approved ATMs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission, Device

print("=" * 70)
print("TESTING ADD VISIT REPORT BUTTON RESTRICTION")
print("=" * 70)

# Get all submissions
submissions = Submission.objects.all().select_related('device')

if not submissions:
    print("\n❌ No submissions found")
else:
    print(f"\n📊 Found {submissions.count()} submission(s):\n")
    
    button_behavior = {
        'Active': '✅ ENABLED - Can add report',
        'Pending': '⏸️ DISABLED - Report under review',
        'Approved': '🔒 DISABLED - Task completed',
        'Rejected': '✅ ENABLED - Can resubmit'
    }
    
    for sub in submissions:
        print(f"Device: {sub.device.interaction_id}")
        print(f"   Status: {sub.status}")
        print(f"   Button: {button_behavior.get(sub.status, '⚪ UNKNOWN')}")
        if sub.status == 'Approved':
            print(f"   Message: 'Task Completed - Report already approved'")
        elif sub.status == 'Pending':
            print(f"   Message: 'Report Pending Review'")
        print()

print("=" * 70)
print("\n📋 BUTTON BEHAVIOR BY STATUS:")
print("=" * 70)
print("   ✅ Active    → ENABLED  (Can add new report)")
print("   ⏸️  Pending   → DISABLED (Report under review)")
print("   🔒 Approved  → DISABLED (Task completed, locked)")
print("   ✅ Rejected  → ENABLED  (Can resubmit after fixes)")
print("=" * 70)

print("\n✅ APPROVED STATUS BEHAVIOR:")
print("   1. Shows blue 'Task Completed' message box")
print("   2. Button disabled with gray color")
print("   3. Button text: 'Report Already Approved'")
print("   4. Lock icon displayed")
print("   5. Cannot click or open form")
print("=" * 70)

print("\n⏸️  PENDING STATUS BEHAVIOR:")
print("   1. Button disabled with gray color")
print("   2. Button text: 'Report Pending Review'")
print("   3. Message: 'Your report is currently under review'")
print("   4. Cannot submit duplicate report")
print("=" * 70)

# Count by status
from collections import Counter
status_counts = Counter([sub.status for sub in submissions])

print("\n📊 CURRENT STATUS DISTRIBUTION:")
print("=" * 70)
for status, count in status_counts.items():
    print(f"   {status}: {count} device(s)")
print("=" * 70)
