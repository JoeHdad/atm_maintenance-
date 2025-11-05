from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with role-based access control.
    """
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('technician', 'Technician'),
        ('supervisor', 'Supervisor'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='technician',
        help_text="User role in the system"
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="City assignment (NULL for host/supervisor)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"


class Device(models.Model):
    """
    ATM device information imported from Excel files.
    """
    MAINTENANCE_TYPE_CHOICES = [
        ('Cleaning1', 'Cleaning1'),
        ('Cleaning2', 'Cleaning2'),
        ('Electrical', 'Electrical'),
        ('Security', 'Security'),
        ('Stand Alone', 'Stand Alone'),
    ]

    interaction_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique device identifier"
    )
    gfm_cost_center = models.CharField(
        max_length=100,
        help_text="Cost center information"
    )
    region = models.CharField(
        max_length=100,
        help_text="Device location region (populated from Excel Status column)"
    )
    gfm_problem_type = models.CharField(
        max_length=100,
        help_text="Problem classification"
    )
    gfm_problem_date = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Problem report date or description"
    )
    city = models.CharField(
        max_length=100,
        help_text="Device location city"
    )
    type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPE_CHOICES,
        help_text="Maintenance type"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['type']),
            models.Index(fields=['city', 'type']),
        ]

    def __str__(self):
        return f"{self.interaction_id} - {self.city}"


class TechnicianDevice(models.Model):
    """
    Links technicians to their assigned devices (many-to-many relationship).
    """
    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_devices',
        help_text="Reference to technician"
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='assigned_technicians',
        help_text="Reference to device"
    )

    class Meta:
        db_table = 'technician_device'
        unique_together = [['technician', 'device']]
        indexes = [
            models.Index(fields=['technician']),
        ]

    def __str__(self):
        return f"{self.technician.username} -> {self.device.interaction_id}"


class Submission(models.Model):
    """
    Tracks maintenance submissions with approval workflow.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Submitting technician"
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Target device"
    )
    type = models.CharField(
        max_length=20,
        choices=Device.MAINTENANCE_TYPE_CHOICES,
        help_text="Maintenance type"
    )
    visit_date = models.DateField(
        help_text="Date of maintenance visit"
    )
    half_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2)],
        help_text="Half-month period (1 or 2)"
    )
    job_status = models.CharField(
        max_length=20,
        choices=[('Ok', 'Ok'), ('Not Ok', 'Not Ok')],
        default='Ok',
        help_text="Job completion status (Ok/Not Ok)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="Approval status (Pending/Approved/Rejected)"
    )
    pdf_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Generated PDF report URL"
    )
    remarks = models.TextField(
        null=True,
        blank=True,
        help_text="Supervisor remarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'submission'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['technician', 'device']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['technician', 'device', 'half_month'],
                condition=~Q(status='Rejected'),
                name='unique_submission_per_half_month_active'
            )
        ]

    def __str__(self):
        return f"Submission {self.id} - {self.device.interaction_id} ({self.half_month})"


class Photo(models.Model):
    """
    Stores photo metadata for maintenance submissions.
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='photos',
        help_text="Parent submission"
    )
    section = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        help_text="Photo section (1-3)"
    )
    file_url = models.URLField(
        max_length=500,
        help_text="Photo file URL"
    )
    order_index = models.IntegerField(
        help_text="Photo order within section"
    )

    class Meta:
        db_table = 'photo'
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['submission', 'section']),
        ]

    def __str__(self):
        return f"Photo {self.id} - Section {self.section} (Order {self.order_index})"


class ExcelUpload(models.Model):
    """
    Tracks Excel file uploads by Host for technicians.
    Stores both the file and parsed data for technician access.
    """
    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='excel_uploads',
        help_text="Technician who owns this data"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files',
        help_text="Host user who uploaded the file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original Excel file name"
    )
    file_path = models.CharField(
        max_length=500,
        help_text="Path to stored Excel file"
    )
    device_type = models.CharField(
        max_length=20,
        choices=Device.MAINTENANCE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Device type for this upload"
    )
    parsed_data = models.JSONField(
        help_text="Parsed Excel data stored as JSON"
    )
    row_count = models.IntegerField(
        default=0,
        help_text="Number of rows in Excel file"
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the file was uploaded"
    )
    
    class Meta:
        db_table = 'excel_upload'
        indexes = [
            models.Index(fields=['technician']),
            models.Index(fields=['upload_date']),
        ]
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.file_name} - {self.technician.username} ({self.upload_date.strftime('%Y-%m-%d')})"
