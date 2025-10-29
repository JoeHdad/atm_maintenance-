"""
Simple test script to send an actual email to yossefhaddad20@gmail.com
This will test the complete email sending functionality with PDF attachment
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import Submission
from core.utils.email_sender import send_approval_email
from core.utils.pdf_generator import generate_pdf
from django.conf import settings

print("=" * 70)
print("EMAIL SENDING TEST - ACTUAL EMAIL TO yossefhaddad20@gmail.com")
print("=" * 70)

# Check email configuration
print("\n📧 Current Email Configuration:")
print(f"   Host: {settings.EMAIL_HOST}")
print(f"   Port: {settings.EMAIL_PORT}")
print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
print(f"   To: {', '.join(settings.APPROVAL_EMAIL_RECIPIENTS)}")
print(f"   User: {settings.EMAIL_HOST_USER}")

if not settings.EMAIL_HOST_USER or settings.EMAIL_HOST_USER == 'your-email@gmail.com':
    print("\n" + "=" * 70)
    print("⚠️  GMAIL CREDENTIALS NOT CONFIGURED")
    print("=" * 70)
    print("\nTo send actual emails, you need to configure Gmail credentials:")
    print("\n1️⃣  Get Gmail App Password:")
    print("   • Go to: https://myaccount.google.com/apppasswords")
    print("   • Sign in to your Gmail account")
    print("   • Create app password for 'Mail'")
    print("   • Copy the 16-character password")
    print("\n2️⃣  Update backend/.env file:")
    print("   EMAIL_HOST_USER=your-actual-email@gmail.com")
    print("   EMAIL_HOST_PASSWORD=your-16-char-app-password")
    print("\n3️⃣  Restart this script")
    print("\n" + "=" * 70)
    exit(0)

if not settings.EMAIL_HOST_PASSWORD or settings.EMAIL_HOST_PASSWORD == 'your-app-password':
    print("\n" + "=" * 70)
    print("⚠️  GMAIL PASSWORD NOT CONFIGURED")
    print("=" * 70)
    print("\nPlease update EMAIL_HOST_PASSWORD in backend/.env file")
    print("Use the 16-character App Password from Gmail")
    print("=" * 70)
    exit(0)

print("\n✅ Email credentials configured!")

# Get or create test submission with PDF
print("\n" + "=" * 70)
print("📄 Preparing Test Submission")
print("=" * 70)

submission = Submission.objects.first()

if not submission:
    print("\n❌ No submissions found in database")
    print("   Please create a submission first")
    exit(1)

print(f"\n✅ Found Submission:")
print(f"   ID: {submission.id}")
print(f"   Device: {submission.device.interaction_id}")
print(f"   Cost Center: {submission.device.gfm_cost_center}")
print(f"   Technician: {submission.technician.username}")
print(f"   Status: {submission.status}")

# Generate PDF if not exists
if not submission.pdf_url:
    print("\n🔄 Generating PDF...")
    try:
        pdf_path = generate_pdf(submission)
        submission.pdf_url = pdf_path
        submission.save()
        print(f"   ✅ PDF generated: {pdf_path}")
    except Exception as e:
        print(f"   ❌ PDF generation failed: {str(e)}")
        exit(1)
else:
    print(f"\n✅ PDF already exists: {submission.pdf_url}")

# Check if PDF file exists
pdf_full_path = submission.pdf_url if os.path.isabs(submission.pdf_url) else os.path.join(os.getcwd(), submission.pdf_url)
if not os.path.exists(pdf_full_path):
    print(f"\n❌ PDF file not found at: {pdf_full_path}")
    exit(1)

pdf_size_mb = os.path.getsize(pdf_full_path) / (1024 * 1024)
print(f"   PDF Size: {pdf_size_mb:.2f} MB")

# Confirm before sending
print("\n" + "=" * 70)
print("📧 READY TO SEND EMAIL")
print("=" * 70)
print(f"\n   From: {settings.DEFAULT_FROM_EMAIL}")
print(f"   To: {', '.join(settings.APPROVAL_EMAIL_RECIPIENTS)}")
print(f"   Subject: ATM {submission.type} Report – {submission.device.interaction_id} – Half {submission.half_month}")
print(f"   Attachment: ATM_Report_{submission.device.interaction_id}_{submission.created_at.strftime('%Y%m%d')}.pdf ({pdf_size_mb:.2f} MB)")

print("\n" + "=" * 70)
confirm = input("\n⚠️  Do you want to send this email? (yes/no): ")
print("=" * 70)

if confirm.lower() != 'yes':
    print("\n❌ Email sending cancelled")
    exit(0)

# Send email
print("\n🔄 Sending email...")
print("   This may take a few seconds...")

try:
    result = send_approval_email(submission)
    
    print("\n" + "=" * 70)
    print("📊 EMAIL SENDING RESULT")
    print("=" * 70)
    
    if result['success']:
        print("\n✅ ✅ ✅ EMAIL SENT SUCCESSFULLY! ✅ ✅ ✅")
        print(f"\n   Message: {result['message']}")
        print(f"   Recipients: {', '.join(result['recipients'])}")
        print("\n📬 Please check the inbox at: yossefhaddad20@gmail.com")
        print("   (Check spam folder if not in inbox)")
    else:
        print("\n❌ EMAIL SENDING FAILED")
        print(f"\n   Error: {result['message']}")
        print(f"   Recipients: {', '.join(result['recipients']) if result['recipients'] else 'N/A'}")
        
        if "Username and Password not accepted" in result['message']:
            print("\n💡 Troubleshooting:")
            print("   • Make sure you're using Gmail App Password (not regular password)")
            print("   • Enable 2-Step Verification in Gmail")
            print("   • Generate new App Password at: https://myaccount.google.com/apppasswords")
        elif "Connection refused" in result['message']:
            print("\n💡 Troubleshooting:")
            print("   • Check your internet connection")
            print("   • Verify SMTP settings (smtp.gmail.com:587)")
        
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ UNEXPECTED ERROR")
    print("=" * 70)
    print(f"\n   {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
