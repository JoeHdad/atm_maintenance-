import os
import sys
import django

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission
from core.utils.email_sender import send_approval_email
from django.conf import settings

print("=" * 60)
print("TESTING EMAIL SENDING")
print("=" * 60)

# Check email configuration
print("\n📧 Email Configuration:")
print(f"  Backend: {settings.EMAIL_BACKEND}")
print(f"  Host: {settings.EMAIL_HOST}")
print(f"  Port: {settings.EMAIL_PORT}")
print(f"  Use TLS: {settings.EMAIL_USE_TLS}")
print(f"  From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"  Host User: {settings.EMAIL_HOST_USER or '(Not configured)'}")

# Debug: print available settings
print("\nDEBUG: Available settings attributes:")
for attr in dir(settings):
    if not attr.startswith('_'):
        print(f"  {attr}")

print(f"\nDEBUG: APPROVAL_EMAIL_RECIPIENTS in settings: {hasattr(settings, 'APPROVAL_EMAIL_RECIPIENTS')}")
if hasattr(settings, 'APPROVAL_EMAIL_RECIPIENTS'):
    print(f"  Value: {settings.APPROVAL_EMAIL_RECIPIENTS}")
    print(f"  Recipients: {', '.join(settings.APPROVAL_EMAIL_RECIPIENTS)}")
else:
    print("  Not found!")
    print("  Recipients: N/A")

# Get a test submission with PDF
submissions = Submission.objects.filter(pdf_url__isnull=False)

if not submissions.exists():
    print("\n⚠️  No submissions with PDF found.")
    print("   Generating PDF first...")
    from core.utils.pdf_generator import generate_pdf
    
    submission = Submission.objects.first()
    if submission:
        try:
            pdf_path = generate_pdf(submission)
            submission.pdf_url = pdf_path
            submission.save()
            print(f"   ✅ PDF generated: {pdf_path}")
        except Exception as e:
            print(f"   ❌ PDF generation failed: {str(e)}")
            exit(1)
    else:
        print("   ❌ No submissions found in database")
        exit(1)
else:
    submission = submissions.first()

print(f"\n📄 Test Submission:")
print(f"  ID: {submission.id}")
print(f"  Device: {submission.device.interaction_id}")
print(f"  Cost Center: {submission.device.gfm_cost_center}")
print(f"  Technician: {submission.technician.username}")
print(f"  Status: {submission.status}")
print(f"  PDF URL: {submission.pdf_url}")

# Check if PDF file exists
pdf_full_path = submission.pdf_url if os.path.isabs(submission.pdf_url) else os.path.join(settings.PDF_BASE_DIR, submission.pdf_url.lstrip('media/pdfs/'))
pdf_exists = os.path.exists(pdf_full_path)
print(f"  PDF Exists: {pdf_exists}")

if not pdf_exists:
    print(f"\n❌ PDF file not found at: {pdf_full_path}")
    exit(1)

# Check email credentials
if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("\n⚠️  EMAIL CREDENTIALS NOT CONFIGURED")
    print("   To actually send emails, you need to:")
    print("   1. Update backend/.env file:")
    print("      EMAIL_HOST_USER=your-email@gmail.com")
    print("      EMAIL_HOST_PASSWORD=your-app-password")
    print("   2. For Gmail, use App Password (not regular password)")
    print("      https://support.google.com/accounts/answer/185833")
    print("\n   For now, testing email composition without sending...")
    
    # Test email composition
    print("\n🔄 Testing email composition...")
    try:
        result = send_approval_email(submission)
        print(f"\n📊 Email Composition Result:")
        print(f"  Success: {result['success']}")
        print(f"  Message: {result['message']}")
        print(f"  Recipients: {result['recipients']}")
        
        if result['success']:
            print("\n✅ Email composition successful!")
            print("   Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to actually send emails.")
        else:
            print(f"\n❌ Email composition failed: {result['message']}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("\n🔄 Sending email...")
    print("   This will actually send an email to the configured recipients.")
    
    # Auto-confirm for testing
    confirm = 'yes'
    
    if confirm.lower() == 'yes':
        try:
            result = send_approval_email(submission)
            print(f"\n📊 Email Sending Result:")
            print(f"  Success: {result['success']}")
            print(f"  Message: {result['message']}")
            print(f"  Recipients: {result['recipients']}")
            
            if result['success']:
                print("\n✅ Email sent successfully!")
            else:
                print(f"\n❌ Email sending failed: {result['message']}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("\n   Email sending cancelled.")

print("\n" + "=" * 60)
