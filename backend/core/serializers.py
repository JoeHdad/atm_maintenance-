from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Device, TechnicianDevice, Submission, Photo
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with JWT token generation.
    """
    username = serializers.CharField(
        required=True,
        help_text="User's username"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="User's password"
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'Invalid username or password',
                    code='invalid_credentials'
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    'Your account has been disabled. Please contact support.',
                    code='account_disabled'
                )
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Please provide both username and password',
                code='missing_credentials'
            )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information in responses.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'city']
        read_only_fields = ['id', 'username', 'role', 'city']


class TechnicianCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating technician accounts by Data Host.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="Password must be at least 8 characters"
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'city', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']
    
    def validate_username(self, value):
        """
        Validate username is unique and alphanumeric (allows underscores).
        """
        # Check alphanumeric (allow underscores)
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username must contain only letters, numbers, and underscores"
            )
        
        # Check uniqueness
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists"
            )
        
        return value
    
    def validate_password(self, value):
        """
        Validate password strength using Django's validators.
        """
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value
    
    def validate_city(self, value):
        """
        Validate city is provided and not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("City is required")
        
        return value.strip()
    
    def create(self, validated_data):
        """
        Create technician user with hashed password.
        """
        # Extract password
        password = validated_data.pop('password')
        
        # Create user instance without saving
        user = User(
            username=validated_data.get('username'),
            city=validated_data.get('city'),
            role='technician'
        )
        
        # Set password (this hashes it)
        user.set_password(password)
        
        # Save to database
        user.save()
        
        return user


class ExcelUploadSerializer(serializers.Serializer):
    """
    Serializer for Excel file upload with device data.
    """
    file = serializers.FileField(
        required=True,
        help_text="Excel file (.xlsx or .xls)"
    )
    technician_id = serializers.IntegerField(
        required=True,
        help_text="ID of the technician to assign devices to"
    )
    device_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Device.MAINTENANCE_TYPE_CHOICES],
        required=True,
        help_text="Type of maintenance (Cleaning1, Cleaning2, Electrical, Security, or Stand Alone)"
    )
    
    def validate_technician_id(self, value):
        """
        Validate that the technician exists and has the correct role.
        """
        try:
            technician = User.objects.get(id=value, role='technician')
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"Technician with ID {value} does not exist"
            )
        
        return value
    
    def validate_file(self, value):
        """
        Validate file extension.
        """
        allowed_extensions = ['.xlsx', '.xls']
        file_name = value.name.lower()
        
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for Device model.
    """
    class Meta:
        model = Device
        fields = [
            'id',
            'interaction_id',
            'gfm_cost_center',
            'region',
            'gfm_problem_type',
            'gfm_problem_date',
            'city',
            'type',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DeviceListSerializer(serializers.ModelSerializer):
    """
    Serializer for technician device list with submission status and next due date.
    """
    submission_status = serializers.SerializerMethodField()
    next_due_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = [
            'id',
            'interaction_id',
            'gfm_cost_center',
            'region',
            'gfm_problem_type',
            'gfm_problem_date',
            'city',
            'type',
            'submission_status',
            'next_due_date',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_submission_status(self, obj):
        """
        Check if device has been submitted for current half_month.
        Returns: 'submitted' or 'pending'
        """
        # Get current date and calculate half_month
        today = date.today()
        current_half_month = 1 if today.day <= 15 else 2
        
        # Get technician from context
        request = self.context.get('request')
        if not request or not request.user:
            return 'pending'
        
        # Check if submission exists for current half_month
        submission_exists = Submission.objects.filter(
            device=obj,
            technician=request.user,
            visit_date__year=today.year,
            visit_date__month=today.month,
            half_month=current_half_month
        ).exists()
        
        return 'submitted' if submission_exists else 'pending'
    
    def get_next_due_date(self, obj):
        """
        Calculate next due date based on maintenance type.
        - Cleaning1, Cleaning2: Next half_month (1 or 2) within current month or next month
        - Electrical, Security: Next month if already submitted this month
        """
        today = date.today()
        current_half_month = 1 if today.day <= 15 else 2
        
        # Get technician from context
        request = self.context.get('request')
        if not request or not request.user:
            return None
        
        # Cleaning types use half-month scheduling
        if obj.type in ['Cleaning1', 'Cleaning2']:
            # Check if submitted for current half_month
            submitted_current = Submission.objects.filter(
                device=obj,
                technician=request.user,
                visit_date__year=today.year,
                visit_date__month=today.month,
                half_month=current_half_month
            ).exists()
            
            if not submitted_current:
                # Next due is current half_month
                return {
                    'date': today.isoformat(),
                    'half_month': current_half_month,
                    'description': f'Half {current_half_month} of {today.strftime("%B %Y")}'
                }
            else:
                # Next due is next half_month
                if current_half_month == 1:
                    # Next is half 2 of current month
                    return {
                        'date': date(today.year, today.month, 16).isoformat(),
                        'half_month': 2,
                        'description': f'Half 2 of {today.strftime("%B %Y")}'
                    }
                else:
                    # Next is half 1 of next month
                    next_month = today + relativedelta(months=1)
                    return {
                        'date': date(next_month.year, next_month.month, 1).isoformat(),
                        'half_month': 1,
                        'description': f'Half 1 of {next_month.strftime("%B %Y")}'
                    }
        
        # Electrical and Security types use monthly scheduling
        elif obj.type in ['Electrical', 'Security']:
            # Check if submitted this month
            submitted_this_month = Submission.objects.filter(
                device=obj,
                technician=request.user,
                visit_date__year=today.year,
                visit_date__month=today.month
            ).exists()
            
            if not submitted_this_month:
                # Next due is this month
                return {
                    'date': today.isoformat(),
                    'month': today.strftime("%B %Y"),
                    'description': f'{today.strftime("%B %Y")}'
                }
            else:
                # Next due is next month
                next_month = today + relativedelta(months=1)
                return {
                    'date': date(next_month.year, next_month.month, 1).isoformat(),
                    'month': next_month.strftime("%B %Y"),
                    'description': f'{next_month.strftime("%B %Y")}'
                }

        return None


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for Photo model.
    """
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'section', 'file_url', 'order_index']
        read_only_fields = fields

    def get_file_url(self, obj):
        """Return normalized file URL for photo (with forward slashes for web)"""
        # Normalize path separators for web URLs (convert backslashes to forward slashes)
        normalized_path = obj.file_url.replace('\\', '/')
        return normalized_path


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission model with photos.
    """
    photos = PhotoSerializer(many=True, read_only=True)
    technician_name = serializers.CharField(source='technician.username', read_only=True)
    technician_city = serializers.CharField(source='technician.city', read_only=True)
    device_info = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            'id',
            'technician',
            'technician_name',
            'technician_city',
            'device',
            'device_info',
            'type',
            'visit_date',
            'half_month',
            'status',
            'pdf_url',
            'remarks',
            'created_at',
            'photos'
        ]
        read_only_fields = ['id', 'created_at', 'pdf_url']

    def get_device_info(self, obj):
        """Return basic device information"""
        return {
            'interaction_id': obj.device.interaction_id,
            'gfm_cost_center': obj.device.gfm_cost_center,
            'city': obj.device.city,
            'region': obj.device.city,  # Using city as region for now
            'type': obj.device.type
        }


class SubmissionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating maintenance submissions with photo uploads.
    """
    device_id = serializers.IntegerField(required=True)
    visit_date = serializers.DateField(required=True)
    job_description = serializers.CharField(required=True, max_length=200)
    job_status = serializers.ChoiceField(choices=['Ok', 'Not Ok'], required=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_device_id(self, value):
        """Validate that device exists"""
        try:
            device = Device.objects.get(id=value)
            return value
        except Device.DoesNotExist:
            raise serializers.ValidationError(f"Device with ID {value} does not exist")

    def validate(self, attrs):
        """Validate submission data"""
        device_id = attrs.get('device_id')
        visit_date = attrs.get('visit_date')

        # Get technician from context
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User not authenticated")

        technician = request.user

        # Validate device belongs to technician
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device not found")

        # Check if device is assigned to technician
        if not TechnicianDevice.objects.filter(technician=technician, device=device).exists():
            raise serializers.ValidationError("This device is not assigned to you")

        # Calculate half_month from visit_date
        half_month = 1 if visit_date.day <= 15 else 2
        attrs['half_month'] = half_month

        # Check for duplicate submission (same device + same half_month)
        existing_submissions = Submission.objects.filter(
            device=device,
            technician=technician,
            visit_date__year=visit_date.year,
            visit_date__month=visit_date.month,
            half_month=half_month
        )

        non_rejected_submission = existing_submissions.exclude(status='Rejected').first()
        if non_rejected_submission:
            raise serializers.ValidationError(
                f"You have already submitted for this device in half {half_month} of {visit_date.strftime('%B %Y')}"
            )

        rejected_submission = existing_submissions.filter(status='Rejected').order_by('-created_at').first()
        if rejected_submission:
            if rejected_submission.visit_date != visit_date:
                raise serializers.ValidationError(
                    "Your previous submission for this device was rejected. Please resubmit using the same visit date."
                )
            attrs['existing_submission'] = rejected_submission

        attrs['device'] = device
        attrs['technician'] = technician
        attrs['type'] = device.type

        return attrs