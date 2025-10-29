"""
Email Sender for Approved Submissions
Sends email notifications with PDF attachments when submissions are approved
"""
import os
import logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_approval_email(submission):
    """
    Send email notification with PDF attachment for approved submission.
    
    Args:
        submission: Submission model instance
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'recipients': list
        }
    """
    try:
        # Get submission data
        device = submission.device
        technician = submission.technician
        
        # Prepare email subject
        subject = f"ATM {submission.type} Report – {device.interaction_id} – Half {submission.half_month}"
        
        # Prepare email body
        body = f"""
Dear Team,

Please find attached the ATM Maintenance Report for the following device:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBMISSION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ATM ID (GFM):        {device.interaction_id}
Cost Center:         {device.gfm_cost_center}
City:                {device.city}
Type:                {submission.type}
Half Month:          {submission.half_month}

Technician:          {technician.username}
Technician City:     {technician.city}

Visit Date:          {submission.visit_date.strftime('%d/%m/%Y')}
Submission Date:     {submission.created_at.strftime('%d/%m/%Y %H:%M')}
Status:              {submission.status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The attached PDF contains:
• Cover page with visit details
• Section 1: Site Machine photos (3-5m away)
• Section 2: Zoomed front & back photos
• Section 3: Asphalt & pavement photos
• Preventive Cleaning Checklist with inspection results

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated notification from the ATM Maintenance System.
Please do not reply to this email.

Best regards,
ATM Maintenance System
"""
        
        # Get recipients from settings
        recipients = settings.APPROVAL_EMAIL_RECIPIENTS
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        
        # Attach PDF if available
        if submission.pdf_url:
            # PDF URL is relative to project root (e.g., "media/pdfs/1/report.pdf")
            pdf_path = submission.pdf_url if os.path.isabs(submission.pdf_url) else os.path.join(os.getcwd(), submission.pdf_url)
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_filename = f"ATM_Report_{device.interaction_id}_{submission.created_at.strftime('%Y%m%d')}.pdf"
                    email.attach(pdf_filename, pdf_file.read(), 'application/pdf')
                    logger.info(f"PDF attached: {pdf_filename}")
            else:
                logger.warning(f"PDF file not found: {pdf_path}")
                return {
                    'success': False,
                    'message': f'PDF file not found: {pdf_path}',
                    'recipients': recipients
                }
        else:
            logger.warning(f"No PDF URL for submission {submission.id}")
            return {
                'success': False,
                'message': 'No PDF available to attach',
                'recipients': recipients
            }
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f"Email sent successfully for submission {submission.id} to {len(recipients)} recipients")
        
        return {
            'success': True,
            'message': f'Email sent successfully to {len(recipients)} recipient(s)',
            'recipients': recipients
        }
        
    except Exception as e:
        error_msg = f"Email sending failed: {str(e)}"
        logger.error(f"Email sending failed for submission {submission.id}: {str(e)}")
        
        return {
            'success': False,
            'message': error_msg,
            'recipients': getattr(settings, 'APPROVAL_EMAIL_RECIPIENTS', [])
        }


class EmailSenderError(Exception):
    """Custom exception for email sending errors"""
    pass
