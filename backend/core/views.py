from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from .serializers import (
    LoginSerializer, 
    UserSerializer, 
    TechnicianCreateSerializer,
    ExcelUploadSerializer,
    DeviceSerializer,
    DeviceListSerializer,
    SubmissionCreateSerializer,
    SubmissionSerializer
)
from .permissions import IsDataHost, IsTechnician, IsHostOrSupervisor
from .models import User, Device, TechnicianDevice, ExcelUpload, Submission, Photo
from .utils.excel_parser import parse_excel_file, ExcelParserError
from django.db.models import Count
from django.conf import settings
import os
from datetime import datetime


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and return JWT tokens with user information.

    POST /api/auth/login/
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Serialize user data
        user_data = UserSerializer(user).data

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': user_data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that returns the same response format.

    POST /api/auth/refresh/
    """
    pass


@api_view(['GET', 'POST'])
@permission_classes([IsDataHost])
def technicians_view(request):
    """
    Handle both GET and POST for technicians endpoint.
    Only accessible by Data Host users.

    GET /api/host/technicians/ - List all technicians
    POST /api/host/technicians/ - Create new technician
    """
    if request.method == 'GET':
        # List all technicians
        technicians = User.objects.filter(role='technician').order_by('-created_at')
        serializer = UserSerializer(technicians, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Create new technician
        serializer = TechnicianCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            technician = serializer.save()
            
            # Return created technician data (excluding password)
            response_data = {
                'id': technician.id,
                'username': technician.username,
                'role': technician.role,
                'city': technician.city,
                'created_at': technician.created_at
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsDataHost])
def upload_excel(request):
    """
    Upload Excel file, save it to disk, and store parsed data in database.
    Only accessible by Data Host users.
    
    POST /api/host/upload-excel
    
    Request (multipart/form-data):
        - file: Excel file (.xlsx or .xls)
        - technician_id: ID of technician (REQUIRED)
        - device_type: 'Cleaning' or 'Electrical' (optional)
    
    Response:
        - upload_id: ID of the ExcelUpload record
        - file_name: Name of the uploaded file
        - total_rows: Number of rows in Excel
        - technician: Technician info
    """
    serializer = ExcelUploadSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract validated data
    excel_file = serializer.validated_data['file']
    technician_id = serializer.validated_data['technician_id']
    device_type = serializer.validated_data.get('device_type')
    
    # Log for debugging
    print(f"[UPLOAD DEBUG] Received device_type: {device_type}")
    print(f"[UPLOAD DEBUG] Technician ID: {technician_id}")
    
    # Technician is now REQUIRED
    if not technician_id:
        return Response(
            {'error': 'technician_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get technician (REQUIRED)
        try:
            technician = User.objects.get(id=technician_id, role='technician')
        except User.DoesNotExist:
            return Response(
                {'error': f'Technician with ID {technician_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parse Excel file
        try:
            parsed_data, row_count = parse_excel_file(excel_file, excel_file.name)
        except ExcelParserError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'excel_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = os.path.splitext(excel_file.name)[1]
        unique_filename = f"{technician.username}_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file to disk
        with open(file_path, 'wb+') as destination:
            for chunk in excel_file.chunks():
                destination.write(chunk)
        
        # Store relative path for database
        relative_path = os.path.join('excel_uploads', unique_filename)
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Check if an upload already exists for this technician and device type
            existing_upload = ExcelUpload.objects.filter(
                technician=technician,
                device_type=device_type
            ).first()
            
            if existing_upload:
                # Update existing upload
                print(f"[UPLOAD DEBUG] Updating existing upload for device_type: {device_type}")
                print(f"[UPLOAD DEBUG] Existing upload ID: {existing_upload.id}")
                existing_upload.uploaded_by = request.user
                existing_upload.file_name = excel_file.name
                existing_upload.file_path = relative_path
                existing_upload.parsed_data = parsed_data
                existing_upload.row_count = row_count
                existing_upload.upload_date = datetime.now()
                existing_upload.save()
                excel_upload = existing_upload
                print(f"[UPLOAD DEBUG] Updated upload ID: {excel_upload.id}, device_type: {excel_upload.device_type}")
            else:
                # Create new ExcelUpload record
                print(f"[UPLOAD DEBUG] Creating new upload for device_type: {device_type}")
                excel_upload = ExcelUpload.objects.create(
                    technician=technician,
                    uploaded_by=request.user,
                    file_name=excel_file.name,
                    file_path=relative_path,
                    device_type=device_type,
                    parsed_data=parsed_data,
                    row_count=row_count
                )
                print(f"[UPLOAD DEBUG] Created upload with ID: {excel_upload.id}, device_type: {excel_upload.device_type}")
            
            # Verify what's actually in the database
            all_uploads_for_tech = ExcelUpload.objects.filter(technician=technician)
            print(f"[UPLOAD DEBUG] Total uploads for technician {technician.id} after save: {all_uploads_for_tech.count()}")
            for upload in all_uploads_for_tech:
                print(f"[UPLOAD DEBUG]   - ID: {upload.id}, device_type: '{upload.device_type}', file: {upload.file_name}")

            # Create Device records from Excel data
            from .models import TechnicianDevice, Device

            # If replacing data, remove previous assignments for this technician & device type
            existing_assignments = TechnicianDevice.objects.filter(
                technician=technician,
                device__type=device_type
            )

            if existing_assignments.exists():
                assignment_count = existing_assignments.count()
                device_ids = list(existing_assignments.values_list('device_id', flat=True))
                print(f"[UPLOAD DEBUG] Removing {assignment_count} existing assignments for device_type '{device_type}'")
                existing_assignments.delete()

                # Clean up orphan devices (no remaining technician assignments)
                removed_devices = 0
                for device_id in device_ids:
                    if not TechnicianDevice.objects.filter(device_id=device_id).exists():
                        Device.objects.filter(id=device_id).delete()
                        removed_devices += 1
                print(f"[UPLOAD DEBUG] Removed {removed_devices} orphan device records for device_type '{device_type}'")

            devices_created = 0

            for index, row in enumerate(parsed_data):
                # Skip header row
                if index == 0:
                    first_value = row.get('col_1', '')
                    if isinstance(first_value, str) and (
                        'interaction' in first_value.lower() or 
                        'id' in first_value.lower() or
                        'gfm' in first_value.lower()
                    ):
                        continue
                
                # Extract device data from Excel row
                interaction_id = row.get('col_1', '')
                gfm_cost_center = row.get('col_2', '')
                gfm_problem_type = row.get('col_3', '')
                gfm_problem_date = row.get('col_4', '')
                city = row.get('col_5', '')
                
                # Skip if no interaction_id
                if not interaction_id or interaction_id == 'N/A':
                    continue
                
                # Check if device already exists
                device, created = Device.objects.get_or_create(
                    interaction_id=interaction_id,
                    defaults={
                        'gfm_cost_center': gfm_cost_center or '',
                        'gfm_problem_type': gfm_problem_type or '',
                        'gfm_problem_date': gfm_problem_date or '',
                        'city': city or '',
                        'type': device_type or 'Cleaning1',
                    }
                )
                
                # Assign device to technician (if not already assigned)
                TechnicianDevice.objects.get_or_create(
                    technician=technician,
                    device=device
                )
                
                if created:
                    devices_created += 1
        
        # Log final state before response
        print(f"[UPLOAD DEBUG] ========================================")
        print(f"[UPLOAD DEBUG] Upload complete for technician {technician.id}")
        print(f"[UPLOAD DEBUG] Uploaded device_type: {device_type}")
        print(f"[UPLOAD DEBUG] Upload ID: {excel_upload.id}")
        print(f"[UPLOAD DEBUG] ========================================")
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': 'Excel file uploaded and devices created successfully',
            'upload_id': excel_upload.id,
            'file_name': excel_file.name,
            'total_rows': row_count,
            'devices_created': devices_created,
            'data': parsed_data[:10],  # Return first 10 rows for preview
            'technician': {
                'id': technician.id,
                'username': technician.username,
                'city': technician.city
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsHostOrSupervisor])
def dashboard_stats(request):
    """
    Get dashboard statistics for Data Host and Supervisors.
    Accessible by both Data Host and Supervisor users for monitoring.
    
    GET /api/host/dashboard-stats
    
    Response:
        - total_technicians: Total number of technician accounts
        - total_devices: Total number of devices in system
        - technicians_with_devices: List of technicians with device counts
    """
    try:
        # Count total technicians
        total_technicians = User.objects.filter(role='technician').count()
        
        # Count total devices
        total_devices = Device.objects.count()
        
        # Get technicians with device counts (top 10 most recent)
        technicians_with_devices = User.objects.filter(
            role='technician'
        ).annotate(
            device_count=Count('assigned_devices')
        ).values(
            'id', 'username', 'city', 'device_count', 'created_at'
        ).order_by('-created_at')[:10]
        
        response_data = {
            'total_technicians': total_technicians,
            'total_devices': total_devices,
            'technicians_with_devices': list(technicians_with_devices)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch dashboard stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsTechnician])
def get_my_excel_data(request):
    """
    Get Excel data uploaded for the logged-in technician with submission status.
    Only accessible by Technician users.
    
    GET /api/technician/my-excel-data
    
    Response:
        - uploads: List of Excel uploads for this technician
        - Each upload contains:
          - id: Upload ID
          - file_name: Original file name
          - upload_date: When it was uploaded
          - row_count: Number of rows
          - parsed_data: The actual Excel data with submission status
          - device_type: Type of devices
    """
    try:
        # Get all Excel uploads for this technician
        uploads = ExcelUpload.objects.filter(
            technician=request.user
        ).order_by('-upload_date')
        
        # Get all devices for this technician with their submission status
        # Use the TechnicianDevice relationship
        from .models import TechnicianDevice
        
        technician_devices = TechnicianDevice.objects.filter(
            technician=request.user
        ).select_related('device').prefetch_related('device__submissions')
        
        # Create a map of device_id to submission status and remarks
        device_status_map = {}
        device_remarks_map = {}
        for tech_device in technician_devices:
            device = tech_device.device
            # Get the latest submission for THIS technician for this device (FIXED: added technician filter)
            latest_submission = Submission.objects.filter(
                technician=request.user,
                device=device
            ).order_by('-created_at').first()
            if latest_submission:
                # Return actual status: Active, Pending, Approved, Rejected
                device_status_map[device.interaction_id] = latest_submission.status
                # Include remarks if rejected
                if latest_submission.status == 'Rejected' and latest_submission.remarks:
                    device_remarks_map[device.interaction_id] = latest_submission.remarks
            else:
                device_status_map[device.interaction_id] = 'Active'
        
        # Serialize the data
        uploads_data = []
        for upload in uploads:
            # Add submission status and device_id to each row in parsed_data
            parsed_data_with_status = []
            if upload.parsed_data:
                for row in upload.parsed_data:
                    row_with_status = row.copy()
                    # Get device interaction_id from row (col_1 or col_2)
                    interaction_id = row.get('col_1') or row.get('col_2')
                    
                    # Convert to string for consistent lookup
                    interaction_id_str = str(interaction_id) if interaction_id else None
                    
                    row_with_status['submission_status'] = device_status_map.get(interaction_id_str, 'Active')
                    row_with_status['submission_remarks'] = device_remarks_map.get(interaction_id_str, None)
                    
                    # Add the actual device database ID
                    if interaction_id_str:
                        try:
                            device = Device.objects.get(interaction_id=interaction_id_str)
                            row_with_status['device_id'] = device.id
                        except Device.DoesNotExist:
                            # Try without string conversion in case it's stored differently
                            try:
                                device = Device.objects.get(interaction_id=interaction_id)
                                row_with_status['device_id'] = device.id
                            except Device.DoesNotExist:
                                row_with_status['device_id'] = None
                    else:
                        row_with_status['device_id'] = None
                    
                    parsed_data_with_status.append(row_with_status)
            
            uploads_data.append({
                'id': upload.id,
                'file_name': upload.file_name,
                'upload_date': upload.upload_date,
                'row_count': upload.row_count,
                'device_type': upload.device_type,
                'parsed_data': parsed_data_with_status,
                'uploaded_by': upload.uploaded_by.username if upload.uploaded_by else None
            })
        
        response_data = {
            'technician': {
                'id': request.user.id,
                'username': request.user.username,
                'city': request.user.city
            },
            'total_uploads': len(uploads_data),
            'uploads': uploads_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch Excel data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsTechnician])
def technician_devices_view(request):
    """
    Get list of devices assigned to the authenticated technician.
    Only accessible by Technician users.
    
    GET /api/technician/devices
    
    Query Parameters:
        - type: Filter by device type ('Cleaning', 'Electrical', or 'All')
        - status: Filter by device region/status
    
    Response:
        - count: Total number of devices
        - devices: List of devices with submission status and next due date
    """
    try:
        # Get technician's city
        technician = request.user
        technician_city = technician.city
        
        # Get devices assigned to this technician via TechnicianDevice
        device_ids = TechnicianDevice.objects.filter(
            technician=technician
        ).values_list('device_id', flat=True)
        
        # Base queryset: devices assigned to technician and matching city
        devices = Device.objects.filter(
            id__in=device_ids,
            city=technician_city
        )
        
        # Apply type filter
        device_type = request.query_params.get('type', 'All')
        if device_type and device_type != 'All':
            if device_type in ['Cleaning1', 'Cleaning2', 'Electrical', 'Security', 'Stand Alone']:
                devices = devices.filter(type=device_type)
        
        # Apply status (region) filter
        status_filter = request.query_params.get('status')
        if status_filter:
            devices = devices.filter(region__icontains=status_filter)
        
        # Order by problem date descending
        devices = devices.order_by('-gfm_problem_date')
        
        # Serialize with context for submission status calculation
        serializer = DeviceListSerializer(
            devices, 
            many=True, 
            context={'request': request}
        )
        
        response_data = {
            'count': devices.count(),
            'devices': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch devices: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsTechnician])
def submit_maintenance(request):
    """
    Submit maintenance visit with 8 photos.
    Only accessible by Technician users.
    
    POST /api/technician/submit
    
    Request (multipart/form-data):
        - device_id: ID of the device
        - visit_date: Date of visit (YYYY-MM-DD)
        - job_description: Description of work done
        - status: 'Ok' or 'Not Ok'
        - remarks: Optional remarks
        - section1_1, section1_2, section1_3: Photos for section 1
        - section2_1, section2_2, section2_3: Photos for section 2
        - section3_1, section3_2: Photos for section 3
    
    Response:
        - submission: Created submission with photos
    """
    try:
        # Validate form data
        serializer = SubmissionCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        # Determine if this is an electrical device
        device = validated_data['device']
        gfm_problem_type = (device.gfm_problem_type or '').lower()
        is_electrical = (
            'electro' in gfm_problem_type and 'mechanical' in gfm_problem_type
        ) or 'electrical' in gfm_problem_type or device.type == 'Electrical'
        
        # Check required photos based on device type
        if is_electrical:
            # Electrical: 19 photos (4+4+4+4+3)
            required_photos = [
                'section1_1', 'section1_2', 'section1_3', 'section1_4',
                'section2_1', 'section2_2', 'section2_3', 'section2_4',
                'section3_1', 'section3_2', 'section3_3', 'section3_4',
                'section4_1', 'section4_2', 'section4_3', 'section4_4',
                'section5_1', 'section5_2', 'section5_3'
            ]
        else:
            # Default: 8 photos (3+3+2)
            required_photos = [
                'section1_1', 'section1_2', 'section1_3',
                'section2_1', 'section2_2', 'section2_3',
                'section3_1', 'section3_2'
            ]
        
        missing_photos = []
        for photo_field in required_photos:
            if photo_field not in request.FILES:
                missing_photos.append(photo_field)
        
        if missing_photos:
            return Response(
                {'error': f'Missing required photos: {", ".join(missing_photos)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Check if resubmitting a rejected submission
            existing_submission = validated_data.get('existing_submission')
            
            if existing_submission:
                # Reuse the rejected submission by updating its fields
                submission = existing_submission
                submission.job_status = validated_data['job_status']
                submission.status = 'Pending'  # Reset to Pending for re-review
                submission.remarks = validated_data.get('remarks', '')
                submission.save()
                
                # Delete old photos from disk and database
                from .utils.file_handler import delete_submission_photos, FileHandlerError
                delete_submission_photos(submission.id)
                Photo.objects.filter(submission=submission).delete()
            else:
                # Create new submission with status='Pending' (approval status)
                submission = Submission.objects.create(
                    technician=validated_data['technician'],
                    device=validated_data['device'],
                    type=validated_data['type'],
                    visit_date=validated_data['visit_date'],
                    half_month=validated_data['half_month'],
                    job_status=validated_data['job_status'],  # Ok/Not Ok
                    status='Pending',  # Always Pending until supervisor reviews
                    remarks=validated_data.get('remarks', '')
                )
            
            # Save photos using file handler
            from .utils.file_handler import save_submission_photos, FileHandlerError
            
            try:
                saved_photos = save_submission_photos(request.FILES, submission.id, is_electrical=is_electrical)
                
                # Create Photo records
                for photo_info in saved_photos:
                    Photo.objects.create(
                        submission=submission,
                        section=photo_info['section'],
                        order_index=photo_info['order_index'],
                        file_url=photo_info['file_path']
                    )
                
            except FileHandlerError as e:
                # Rollback will happen automatically due to transaction.atomic()
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Serialize and return the created submission
        response_serializer = SubmissionSerializer(submission)
        
        return Response(
            {
                'status': 'success',
                'message': 'Maintenance submission created successfully',
                'submission': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create submission: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsDataHost])
def get_uploaded_types(request, technician_id):
    """
    Get list of device types that have been uploaded for a specific technician.
    
    GET /api/host/technicians/<technician_id>/uploaded-types
    
    Response:
        - uploaded_types: List of device type strings
    """
    try:
        # Log for debugging
        print(f"[GET_TYPES DEBUG] Fetching uploaded types for technician_id: {technician_id}")
        
        # Get all Excel uploads for this technician
        uploads = ExcelUpload.objects.filter(
            technician_id=technician_id
        ).values_list('device_type', flat=True).distinct()
        
        # Filter out null/empty values and return list
        uploaded_types = [device_type for device_type in uploads if device_type]
        
        print(f"[GET_TYPES DEBUG] Found uploaded types: {uploaded_types}")
        
        # Debug: Show all uploads for this technician
        all_uploads = ExcelUpload.objects.filter(technician_id=technician_id)
        print(f"[GET_TYPES DEBUG] Total uploads: {all_uploads.count()}")
        for upload in all_uploads:
            print(f"[GET_TYPES DEBUG] - Upload ID: {upload.id}, device_type: {upload.device_type}, file: {upload.file_name}")
        
        return Response({
            'uploaded_types': uploaded_types
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch uploaded types: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsDataHost])
def get_uploaded_files(request, technician_id):
    """
    Get detailed information about all uploaded files for a specific technician.
    
    GET /api/host/technicians/<technician_id>/uploaded-files
    
    Response:
        - files: List of file objects with details
    """
    try:
        print(f"[GET_FILES DEBUG] Fetching uploaded files for technician_id: {technician_id}")
        
        # Get all Excel uploads for this technician
        uploads = ExcelUpload.objects.filter(
            technician_id=technician_id
        ).order_by('-upload_date')
        
        files = []
        for upload in uploads:
            files.append({
                'id': upload.id,
                'device_type': upload.device_type,
                'file_name': upload.file_name,
                'upload_date': upload.upload_date,
                'row_count': upload.row_count,
                'uploaded_by': upload.uploaded_by.username if upload.uploaded_by else 'Unknown',
            })
        
        print(f"[GET_FILES DEBUG] Found {len(files)} files")
        
        return Response({
            'files': files
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch uploaded files: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsTechnician])
def get_excel_data_by_type(request, device_type):
    """
    Get Excel data for the logged-in technician filtered by device type.
    
    GET /api/technician/excel-data/<device_type>
    
    Response:
        - data: List of Excel data rows for the specified device type
        - device_type: The requested device type
        - file_name: Name of the Excel file
        - upload_date: When the file was uploaded
    """
    try:
        # Log for debugging
        print(f"[RETRIEVAL DEBUG] ========================================")
        print(f"[RETRIEVAL DEBUG] Fetching data for device_type: '{device_type}'")
        print(f"[RETRIEVAL DEBUG] Device type length: {len(device_type)}")
        print(f"[RETRIEVAL DEBUG] Device type repr: {repr(device_type)}")
        print(f"[RETRIEVAL DEBUG] Technician: {request.user.username} (ID: {request.user.id})")
        
        # Debug: Show all uploads for this technician
        all_uploads = ExcelUpload.objects.filter(technician=request.user)
        print(f"[RETRIEVAL DEBUG] Total uploads for technician: {all_uploads.count()}")
        for upload in all_uploads:
            print(f"[RETRIEVAL DEBUG] - Upload ID: {upload.id}")
            print(f"[RETRIEVAL DEBUG]   device_type: '{upload.device_type}' (repr: {repr(upload.device_type)})")
            print(f"[RETRIEVAL DEBUG]   file: {upload.file_name}")
            print(f"[RETRIEVAL DEBUG]   match: {upload.device_type == device_type}")
        
        # Get Excel uploads for this technician and device type
        uploads = ExcelUpload.objects.filter(
            technician=request.user,
            device_type=device_type
        ).order_by('-upload_date')
        
        print(f"[RETRIEVAL DEBUG] Matching uploads for '{device_type}': {uploads.count()}")
        
        if not uploads.exists():
            return Response({
                'data': [],
                'device_type': device_type,
                'message': f'No Excel data found for device type: {device_type}'
            }, status=status.HTTP_200_OK)
        
        # Get the most recent upload for this device type
        latest_upload = uploads.first()
        print(f"[RETRIEVAL DEBUG] Returning upload ID: {latest_upload.id}")
        print(f"[RETRIEVAL DEBUG] Returning device_type: '{latest_upload.device_type}'")
        print(f"[RETRIEVAL DEBUG] Returning file: {latest_upload.file_name}")
        print(f"[RETRIEVAL DEBUG] Returning rows: {len(latest_upload.parsed_data)}")
        print(f"[RETRIEVAL DEBUG] ========================================")
        
        return Response({
            'data': latest_upload.parsed_data,
            'device_type': device_type,
            'file_name': latest_upload.file_name,
            'upload_date': latest_upload.upload_date
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch Excel data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
