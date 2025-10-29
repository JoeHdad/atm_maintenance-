import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Device, ExcelUpload

print("=== Device Database Check ===")
print(f"Total devices: {Device.objects.count()}")
print("\nFirst 5 devices:")
for device in Device.objects.all()[:5]:
    print(f"  ID: {device.id}, interaction_id: '{device.interaction_id}'")

print("\n=== Excel Upload Check ===")
uploads = ExcelUpload.objects.all()
print(f"Total uploads: {uploads.count()}")

if uploads.exists():
    first_upload = uploads.first()
    print(f"\nFirst upload: {first_upload.file_name}")
    if first_upload.parsed_data:
        print(f"Rows in parsed_data: {len(first_upload.parsed_data)}")
        if len(first_upload.parsed_data) > 0:
            print("\nFirst 3 rows (col_1 values):")
            for i, row in enumerate(first_upload.parsed_data[:3]):
                col_1 = row.get('col_1', 'N/A')
                print(f"  Row {i}: col_1 = '{col_1}' (type: {type(col_1).__name__})")
                
                # Check if device exists with this interaction_id
                try:
                    device = Device.objects.get(interaction_id=str(col_1))
                    print(f"    ✓ Device found: ID={device.id}")
                except Device.DoesNotExist:
                    print(f"    ✗ Device NOT found with interaction_id='{col_1}'")
