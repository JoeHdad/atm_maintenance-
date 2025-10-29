import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission, Photo

print("=" * 60)
print("PHOTO RECORDS CHECK")
print("=" * 60)

submissions = Submission.objects.all()

for sub in submissions:
    print(f"\nSubmission ID: {sub.id}")
    print(f"Device: {sub.device.interaction_id}")
    print(f"Photos: {sub.photos.count()}")
    
    photos = sub.photos.all().order_by('section', 'order_index')
    for photo in photos[:3]:  # Show first 3 photos
        print(f"  - Section {photo.section}, Order {photo.order_index}")
        print(f"    File URL: {photo.file_url}")
        print(f"    Full path: /media/{photo.file_url}")
        
        # Check if file exists
        full_path = os.path.join('media', photo.file_url)
        exists = os.path.exists(full_path)
        print(f"    File exists: {exists}")

print("\n" + "=" * 60)
