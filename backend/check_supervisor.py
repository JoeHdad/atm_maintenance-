import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import User

print("Checking supervisor user...")
admin = User.objects.get(username='admin')
print(f"Username: {admin.username}")
print(f"Role: {admin.role}")
print(f"City: {admin.city}")

if admin.role != 'supervisor':
    print(f"\n⚠️  Fixing role from '{admin.role}' to 'supervisor'")
    admin.role = 'supervisor'
    admin.save()
    print("✅ Role updated!")
