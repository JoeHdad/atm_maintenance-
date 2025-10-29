import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Device, ExcelUpload, User

print("=== Testing get_my_excel_data logic ===\n")

# Get a technician user
technician = User.objects.filter(role='technician').first()
if not technician:
    print("No technician found!")
    exit()

print(f"Testing with technician: {technician.username}")

# Get Excel uploads for this technician
uploads = ExcelUpload.objects.filter(technician=technician).order_by('-upload_date')
print(f"Found {uploads.count()} uploads for this technician\n")

if uploads.exists():
    upload = uploads.first()
    print(f"Testing upload: {upload.file_name}")
    print(f"Parsed data rows: {len(upload.parsed_data)}\n")
    
    # Test the device_id lookup logic
    print("Testing device_id lookup for first 5 rows:")
    for i, row in enumerate(upload.parsed_data[:5]):
        interaction_id = row.get('col_1') or row.get('col_2')
        interaction_id_str = str(interaction_id) if interaction_id else None
        
        print(f"\nRow {i}:")
        print(f"  col_1: '{row.get('col_1')}'")
        print(f"  interaction_id_str: '{interaction_id_str}'")
        
        if interaction_id_str:
            try:
                device = Device.objects.get(interaction_id=interaction_id_str)
                print(f"  ✓ Device found: ID={device.id}")
            except Device.DoesNotExist:
                print(f"  ✗ Device NOT found")
                # Try alternative lookup
                try:
                    device = Device.objects.get(interaction_id=interaction_id)
                    print(f"  ✓ Device found (without str conversion): ID={device.id}")
                except Device.DoesNotExist:
                    print(f"  ✗ Device still NOT found")
        else:
            print(f"  ⚠ No interaction_id")
