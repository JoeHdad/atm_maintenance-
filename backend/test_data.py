import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission, User, Device

print("=" * 60)
print("DATABASE TEST DATA CHECK")
print("=" * 60)

# Check submissions
submissions = Submission.objects.all()
print(f"\n📊 Total Submissions: {submissions.count()}")

if submissions.exists():
    print("\n📋 Submission Details:")
    for s in submissions[:5]:
        print(f"  - ID: {s.id}")
        print(f"    Status: {s.status}")
        print(f"    Device: {s.device.interaction_id}")
        print(f"    Technician: {s.technician.username}")
        print(f"    Visit Date: {s.visit_date}")
        print(f"    Photos: {s.photos.count()}")
        print()

# Check users by role
print("\n👥 Users by Role:")
print(f"  - Hosts: {User.objects.filter(role='host').count()}")
print(f"  - Supervisors: {User.objects.filter(role='supervisor').count()}")
print(f"  - Technicians: {User.objects.filter(role='technician').count()}")

# Check supervisor user
supervisors = User.objects.filter(role='supervisor')
if supervisors.exists():
    print("\n🔍 Supervisor Accounts:")
    for sup in supervisors:
        print(f"  - Username: {sup.username}, City: {sup.city}")
else:
    print("\n⚠️  WARNING: No supervisor account found!")

# Check devices
devices = Device.objects.all()
print(f"\n🏧 Total Devices: {devices.count()}")

print("\n" + "=" * 60)
