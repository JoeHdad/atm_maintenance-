import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Device, ExcelUpload, User

print("=== Testing Complete Device ID Flow ===\n")

# Get a technician with data
technician = User.objects.filter(role='technician', excel_uploads__isnull=False).first()
if not technician:
    print("No technician with uploads found!")
    exit()

print(f"Testing with technician: {technician.username}\n")

# Get their Excel uploads
uploads = ExcelUpload.objects.filter(technician=technician)
print(f"Found {uploads.count()} uploads\n")

if uploads.exists():
    upload = uploads.first()
    print(f"Upload: {upload.file_name}")
    print(f"Device type: {upload.device_type}")
    print(f"Total rows: {len(upload.parsed_data)}\n")
    
    print("Testing first 5 rows:")
    print("-" * 80)
    
    for i, row in enumerate(upload.parsed_data[:5]):
        col_1 = row.get('col_1', 'N/A')
        col_2 = row.get('col_2', 'N/A')
        
        # Simulate backend logic
        interaction_id = col_1 or col_2
        interaction_id_str = str(interaction_id) if interaction_id else None
        
        device_id = None
        if interaction_id_str:
            try:
                device = Device.objects.get(interaction_id=interaction_id_str)
                device_id = device.id
            except Device.DoesNotExist:
                try:
                    device = Device.objects.get(interaction_id=interaction_id)
                    device_id = device.id
                except Device.DoesNotExist:
                    pass
        
        print(f"\nRow {i}:")
        print(f"  col_1: '{col_1}'")
        print(f"  col_2: '{col_2}'")
        print(f"  interaction_id_str: '{interaction_id_str}'")
        print(f"  device_id: {device_id}")
        
        if device_id:
            print(f"  ✅ Would be sent to frontend with device_id={device_id}")
        else:
            print(f"  ⚠️  Would be sent to frontend with device_id=None (will be filtered out)")

print("\n" + "=" * 80)
print("\nConclusion:")
print("- Rows with device_id=None should be filtered out by frontend")
print("- Rows with device_id=<number> should appear in dashboard")
print("- When user clicks on a device, it should have the id field set")
