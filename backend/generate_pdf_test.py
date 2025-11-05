import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
import django
django.setup()
from core.models import Submission
from core.utils.pdf_generator import generate_pdf

try:
    submission = Submission.objects.get(id=1)
    pdf_path = generate_pdf(submission)
    # Update the submission pdf_url to the new path
    submission.pdf_url = pdf_path.replace('\\', '/')
    submission.save()
    print(f'PDF generated and updated: {pdf_path}')
    print(f'Submission pdf_url: {submission.pdf_url}')
    print(f'PDF exists: {os.path.exists(pdf_path)}')
except Exception as e:
    print(f'Error: {e}')
