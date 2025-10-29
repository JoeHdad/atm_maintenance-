import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission
from core.utils.pdf_generator import generate_pdf

print("=" * 60)
print("TESTING PDF GENERATION")
print("=" * 60)

# Get a test submission
submissions = Submission.objects.filter(status='Pending')

if not submissions.exists():
    print("\n⚠️  No pending submissions found. Creating test data...")
    submissions = Submission.objects.all()

if submissions.exists():
    submission = submissions.first()
    
    print(f"\nTest Submission:")
    print(f"  ID: {submission.id}")
    print(f"  Device: {submission.device.interaction_id}")
    print(f"  Cost Center: {submission.device.gfm_cost_center}")
    print(f"  Technician: {submission.technician.username}")
    print(f"  Photos: {submission.photos.count()}")
    print(f"  Status: {submission.status}")
    
    print("\n🔄 Generating PDF...")
    
    try:
        pdf_path = generate_pdf(submission)
        print(f"\n✅ PDF Generated Successfully!")
        print(f"   Path: {pdf_path}")
        
        # Check if file exists
        full_path = os.path.join('media', pdf_path) if not pdf_path.startswith('media') else pdf_path
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"   File Size: {file_size / 1024:.2f} KB")
            print(f"   Full Path: {os.path.abspath(full_path)}")
        else:
            print(f"   ⚠️  File not found at: {full_path}")
        
    except Exception as e:
        print(f"\n❌ PDF Generation Failed!")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ No submissions found in database")

print("\n" + "=" * 60)
