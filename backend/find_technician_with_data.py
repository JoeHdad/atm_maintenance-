import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import ExcelUpload, User

print("=== Finding technicians with Excel uploads ===\n")

# Get all Excel uploads
uploads = ExcelUpload.objects.all()
print(f"Total uploads: {uploads.count()}\n")

# Group by technician
from collections import defaultdict
tech_uploads = defaultdict(list)

for upload in uploads:
    if upload.technician:
        tech_uploads[upload.technician.username].append(upload.file_name)

print("Technicians with uploads:")
for username, files in tech_uploads.items():
    print(f"\n{username}:")
    for file in files:
        print(f"  - {file}")

# Pick one technician with data
if tech_uploads:
    test_username = list(tech_uploads.keys())[0]
    print(f"\n\n=== Testing with: {test_username} ===")
    
    technician = User.objects.get(username=test_username)
    uploads = ExcelUpload.objects.filter(technician=technician)
    
    if uploads.exists():
        upload = uploads.first()
        print(f"Upload: {upload.file_name}")
        print(f"Rows: {len(upload.parsed_data)}")
        
        print("\nFirst 5 rows with device_id lookup:")
        from core.models import Device
        
        for i, row in enumerate(upload.parsed_data[:5]):
            interaction_id = row.get('col_1') or row.get('col_2')
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
            
            print(f"Row {i}: col_1='{row.get('col_1')}' -> device_id={device_id}")
