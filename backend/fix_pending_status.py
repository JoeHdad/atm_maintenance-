"""
Fix existing submissions that have 'Ok' or 'Not Ok' in status field
Move them to job_status and set status to 'Pending'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission

print("=" * 70)
print("FIXING SUBMISSION STATUS ISSUE")
print("=" * 70)

# Find submissions with invalid status
invalid_submissions = Submission.objects.filter(status__in=['Ok', 'Not Ok'])

if not invalid_submissions.exists():
    print("\n✅ No submissions with invalid status found!")
    print("All submissions have correct status values.")
else:
    print(f"\n⚠️  Found {invalid_submissions.count()} submission(s) with invalid status:\n")
    
    for sub in invalid_submissions:
        old_status = sub.status
        print(f"Submission ID {sub.id}:")
        print(f"   Device: {sub.device.interaction_id}")
        print(f"   Current status: '{old_status}' ❌")
        
        # Move status to job_status and set status to Pending
        sub.job_status = old_status  # Ok or Not Ok
        sub.status = 'Pending'  # Set to Pending
        sub.save()
        
        print(f"   Fixed:")
        print(f"      job_status: '{sub.job_status}' ✅")
        print(f"      status: '{sub.status}' ✅")
        print()

print("=" * 70)
print("\n📊 FINAL STATUS CHECK:")
print("=" * 70)

all_submissions = Submission.objects.all()
for sub in all_submissions:
    status_color = {
        'Pending': '🟠',
        'Approved': '🔵',
        'Rejected': '🔴'
    }.get(sub.status, '⚪')
    
    job_color = '✅' if sub.job_status == 'Ok' else '❌'
    
    print(f"ID {sub.id} | Device: {sub.device.interaction_id}")
    print(f"   Status: {status_color} {sub.status}")
    print(f"   Job Status: {job_color} {sub.job_status}")
    print()

print("=" * 70)
print("\n✅ STATUS FIELDS EXPLANATION:")
print("=" * 70)
print("   📋 status: Approval workflow (Pending/Approved/Rejected)")
print("      - Pending: Awaiting supervisor review")
print("      - Approved: Supervisor approved the report")
print("      - Rejected: Supervisor rejected the report")
print()
print("   🔧 job_status: Job completion (Ok/Not Ok)")
print("      - Ok: Job completed successfully")
print("      - Not Ok: Job had issues")
print("=" * 70)

print("\n✅ Fix completed successfully!")
