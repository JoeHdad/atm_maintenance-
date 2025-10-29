import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Device

print("=" * 60)
print("DEVICE DATA CHECK")
print("=" * 60)

devices = Device.objects.all()[:5]

for device in devices:
    print(f"\nDevice: {device.interaction_id}")
    print(f"  Cost Center: {device.gfm_cost_center}")
    print(f"  City: {device.city}")
    print(f"  Type: {device.type}")

print("\n" + "=" * 60)
