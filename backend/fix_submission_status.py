import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission

print("=" * 70)
print("FIXING SUBMISSION STATUSES")
print("=" * 70)

# Find submissions with invalid status
invalid_submissions = Submission.objects.exclude(status__in=['Pending', 'Approved', 'Rejected'])

if not invalid_submissions:
    print("\n✅ All submissions have valid statuses")
else:
    print(f"\n⚠️  Found {invalid_submissions.count()} submission(s) with invalid status:\n")
    for sub in invalid_submissions:
        print(f"ID: {sub.id}")
        print(f"   Device: {sub.device.interaction_id}")
        print(f"   Current Status: '{sub.status}'")
        print(f"   Fixing to: 'Pending'")
        
        # Fix the status
        sub.status = 'Pending'
        sub.save()
        
        print(f"   ✅ Fixed!\n")

print("=" * 70)
print("\n📊 Current Submission Statuses:")
print("=" * 70)

all_submissions = Submission.objects.all()
for sub in all_submissions:
    print(f"ID: {sub.id} | Device: {sub.device.interaction_id} | Status: {sub.status}")

print("\n" + "=" * 70)
