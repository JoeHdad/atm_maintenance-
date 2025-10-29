import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission

print("=" * 70)
print("CHECKING SUBMISSION STATUSES")
print("=" * 70)

submissions = Submission.objects.all()

if not submissions:
    print("\n❌ No submissions found in database")
else:
    print(f"\n📊 Found {submissions.count()} submission(s):\n")
    for sub in submissions:
        print(f"ID: {sub.id}")
        print(f"   Device: {sub.device.interaction_id}")
        print(f"   Status: {sub.status}")
        print(f"   Created: {sub.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Technician: {sub.technician.username}")
        print()

print("=" * 70)
print("\n💡 NOTE:")
print("   Approve/Reject buttons only appear for submissions with status='Pending'")
print("   If all submissions are already Approved/Rejected, buttons won't show")
print("=" * 70)
