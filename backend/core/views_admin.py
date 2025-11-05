"""
Admin/Supervisor views for reviewing and approving submissions
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
import logging
import threading

from .models import Submission, Photo
from .serializers import SubmissionSerializer
from .permissions import IsSupervisor
from .utils.pdf_generator import generate_pdf
from .utils.email_sender import send_approval_email

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsSupervisor])
def get_submissions(request):
    """
    Get all submissions for supervisor review.
    
    GET /api/supervisor/submissions
    
    Query Parameters:
        - status: Filter by status (Pending, Approved, Rejected, All)
        - city: Filter by city
        - technician_id: Filter by technician
        - date_from: Filter by visit_date >= date_from (YYYY-MM-DD)
        - date_to: Filter by visit_date <= date_to (YYYY-MM-DD)
    
    Response:
        - submissions: List of submissions with photos
    """
    try:
        # Get query parameters
        submission_status = request.GET.get('status', None)
        city = request.GET.get('city', None)
        technician_id = request.GET.get('technician_id', None)
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        
        # Build query
        queryset = Submission.objects.all().select_related(
            'technician', 'device'
        ).prefetch_related('photos').order_by('-created_at')
        
        # Apply filters
        if submission_status and submission_status != 'All':
            queryset = queryset.filter(status=submission_status)
        
        if city and city != 'All':
            queryset = queryset.filter(device__city=city)
        
        if technician_id:
            queryset = queryset.filter(technician_id=technician_id)
        
        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)
        
        # Serialize
        serializer = SubmissionSerializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'submissions': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch submissions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsSupervisor])
def get_submission_detail(request, submission_id):
    """
    Get detailed information about a specific submission.
    
    GET /api/supervisor/submissions/<id>
    
    Response:
        - submission: Submission details with all photos grouped by section
    """
    try:
        submission = Submission.objects.select_related(
            'technician', 'device'
        ).prefetch_related('photos').get(id=submission_id)
        
        serializer = SubmissionSerializer(submission)
        
        return Response({
            'status': 'success',
            'submission': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Submission.DoesNotExist:
        return Response(
            {'error': 'Submission not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch submission: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsSupervisor])
def approve_submission(request, submission_id):
    """
    Approve a submission.
    
    PATCH /api/supervisor/submissions/<id>/approve
    
    Request:
        - remarks: Optional remarks (optional)
    
    Response:
        - submission: Updated submission
        - pdf_url: Generated PDF URL (stub for now)
        - email_status: Email sending status (stub for now)
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        # Check if already approved
        if submission.status == 'Approved':
            return Response({
                'error': 'Submission is already approved'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status to Approved
        submission.status = 'Approved'
        
        # Add remarks if provided
        if 'remarks' in request.data:
            submission.remarks = request.data['remarks']
        
        submission.save()
        
        # Start background thread for PDF generation and email sending
        def process_approval_async():
            """Background task to generate PDF and send email"""
            try:
                # Generate PDF
                pdf_path = generate_pdf(submission)
                submission.pdf_url = pdf_path
                submission.save()
                logger.info(f"PDF generated for submission {submission_id}: {pdf_path}")
                
                # Send email notification
                email_result = send_approval_email(submission)
                email_status = email_result.get('message')
                email_success = email_result.get('success')
                logger.info(f"Email sent for submission {submission_id}: {email_status} (Success: {email_success})")
            except Exception as e:
                logger.error(f"Background processing failed for submission {submission_id}: {str(e)}")
        
        # Launch async task
        thread = threading.Thread(target=process_approval_async, daemon=True)
        thread.start()
        
        # Serialize response and return immediately
        serializer = SubmissionSerializer(submission)
        
        return Response({
            'status': 'success',
            'message': 'Submission approved successfully. PDF generation and email notification are being processed in the background.',
            'submission': serializer.data,
            'pdf_status': 'Processing in background',
            'email_status': 'Processing in background'
        }, status=status.HTTP_200_OK)
        
    except Submission.DoesNotExist:
        return Response(
            {'error': 'Submission not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error approving submission {submission_id}: {str(e)}")
        return Response(
            {'error': f'Failed to approve submission: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsSupervisor])
def reject_submission(request, submission_id):
    """
    Reject a submission.
    
    PATCH /api/supervisor/submissions/<id>/reject
    
    Request:
        - remarks: Rejection reason (required)
    
    Response:
        - submission: Updated submission
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        # Check if already rejected
        if submission.status == 'Rejected':
            return Response({
                'error': 'Submission is already rejected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate remarks
        if 'remarks' not in request.data or not request.data['remarks']:
            return Response(
                {'error': 'Remarks are required for rejection'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate remarks length
        if len(request.data['remarks'].strip()) < 10:
            return Response(
                {'error': 'Remarks must be at least 10 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to Rejected
        submission.status = 'Rejected'
        submission.remarks = request.data['remarks']
        submission.save()
        
        logger.info(f"Submission {submission_id} rejected by supervisor. Reason: {request.data['remarks'][:50]}...")
        
        serializer = SubmissionSerializer(submission)
        
        return Response({
            'status': 'success',
            'message': 'Submission rejected',
            'submission': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Submission.DoesNotExist:
        return Response(
            {'error': 'Submission not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to reject submission: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsSupervisor])
def preview_pdf(request, submission_id):
    """
    Generate and preview PDF for a submission without approving it.
    
    POST /api/supervisor/submissions/<id>/preview-pdf
    
    Response:
        - pdf_url: URL to the generated preview PDF
        - message: Success message
    """
    try:
        # Prefetch photos to avoid N+1 queries during PDF generation
        submission = Submission.objects.select_related('device', 'technician').prefetch_related('photos').get(id=submission_id)
        
        # Generate PDF preview
        try:
            pdf_path = generate_pdf(submission)
            logger.info(f"Preview PDF generated for submission {submission_id}: {pdf_path}")
            
            return Response({
                'status': 'success',
                'message': 'PDF preview generated successfully',
                'pdf_url': pdf_path
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"PDF preview generation failed for submission {submission_id}: {str(e)}")
            return Response({
                'error': f'Failed to generate PDF preview: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Submission.DoesNotExist:
        return Response(
            {'error': 'Submission not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error generating PDF preview for submission {submission_id}: {str(e)}")
        return Response(
            {'error': f'Failed to generate PDF preview: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsSupervisor])
def get_dashboard_stats(request):
    """
    Get dashboard statistics for supervisor.
    
    GET /api/supervisor/dashboard-stats
    
    Response:
        - total_submissions: Total number of submissions
        - pending_submissions: Number of pending submissions
        - approved_submissions: Number of approved submissions
        - rejected_submissions: Number of rejected submissions
    """
    try:
        # Get submission counts by status
        total_submissions = Submission.objects.count()
        pending_submissions = Submission.objects.filter(status='Pending').count()
        approved_submissions = Submission.objects.filter(status='Approved').count()
        rejected_submissions = Submission.objects.filter(status='Rejected').count()
        
        return Response({
            'total_submissions': total_submissions,
            'pending_submissions': pending_submissions,
            'approved_submissions': approved_submissions,
            'rejected_submissions': rejected_submissions
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return Response(
            {'error': f'Failed to fetch dashboard statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
