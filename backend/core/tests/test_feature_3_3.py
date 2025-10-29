"""
Unit and Integration Tests for Feature 3.3: Device Detail & Photo Upload (Backend)
Tests the POST /api/technician/submit endpoint
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from core.models import Device, TechnicianDevice, Submission, Photo
from core.utils.file_handler import FileHandlerError, validate_photo, save_photo
import os
from django.conf import settings

User = get_user_model()


class FileHandlerTest(TestCase):
    """Test cases for file handler utilities"""
    
    def test_validate_photo_valid_jpg(self):
        """Test that valid JPG photos pass validation"""
        photo = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        photo.size = 1024 * 1024  # 1MB
        
        self.assertTrue(validate_photo(photo))
    
    def test_validate_photo_valid_png(self):
        """Test that valid PNG photos pass validation"""
        photo = SimpleUploadedFile(
            "test.png",
            b"fake image content",
            content_type="image/png"
        )
        photo.size = 1024 * 1024  # 1MB
        
        self.assertTrue(validate_photo(photo))
    
    def test_validate_photo_invalid_format(self):
        """Test that invalid file formats are rejected"""
        photo = SimpleUploadedFile(
            "test.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        photo.size = 1024 * 1024
        
        with self.assertRaises(FileHandlerError):
            validate_photo(photo)
    
    def test_validate_photo_too_large(self):
        """Test that oversized photos are rejected"""
        photo = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        photo.size = 11 * 1024 * 1024  # 11MB (over 10MB limit)
        
        with self.assertRaises(FileHandlerError):
            validate_photo(photo)


class SubmissionCreateTest(TestCase):
    """Test cases for maintenance submission creation"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.technician = User.objects.create_user(
            username='tech1',
            password='testpass123',
            role='technician',
            city='Riyadh'
        )
        
        self.other_technician = User.objects.create_user(
            username='tech2',
            password='testpass123',
            role='technician',
            city='Jeddah'
        )
        
        self.host = User.objects.create_user(
            username='host1',
            password='testpass123',
            role='host'
        )
        
        # Create device
        self.device = Device.objects.create(
            interaction_id='ATM001',
            gfm_cost_center='CC001',
            region='Central',
            gfm_problem_type='Hardware',
            gfm_problem_date=date.today(),
            city='Riyadh',
            type='Cleaning'
        )
        
        # Assign device to technician
        TechnicianDevice.objects.create(technician=self.technician, device=self.device)
        
        # API client
        self.client = APIClient()
        
        # Create test photos
        self.photos = {}
        for i in range(1, 4):
            self.photos[f'section1_{i}'] = SimpleUploadedFile(
                f"section1_{i}.jpg",
                b"fake image content",
                content_type="image/jpeg"
            )
        for i in range(1, 4):
            self.photos[f'section2_{i}'] = SimpleUploadedFile(
                f"section2_{i}.jpg",
                b"fake image content",
                content_type="image/jpeg"
            )
        for i in range(1, 3):
            self.photos[f'section3_{i}'] = SimpleUploadedFile(
                f"section3_{i}.jpg",
                b"fake image content",
                content_type="image/jpeg"
            )
    
    def test_submit_maintenance_success(self):
        """Test successful maintenance submission with all photos"""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            'remarks': 'All systems operational',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('submission', response.data)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify submission was created
        submission = Submission.objects.get(device=self.device, technician=self.technician)
        self.assertEqual(submission.status, 'Ok')
        self.assertEqual(submission.remarks, 'All systems operational')
        
        # Verify 8 photos were created
        photos = Photo.objects.filter(submission=submission)
        self.assertEqual(photos.count(), 8)
    
    def test_submit_maintenance_missing_photos(self):
        """Test that submission fails when photos are missing"""
        self.client.force_authenticate(user=self.technician)
        
        # Only include 5 photos instead of 8
        incomplete_photos = {
            'section1_1': self.photos['section1_1'],
            'section1_2': self.photos['section1_2'],
            'section1_3': self.photos['section1_3'],
            'section2_1': self.photos['section2_1'],
            'section2_2': self.photos['section2_2'],
        }
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **incomplete_photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Missing required photos', response.data['error'])
    
    def test_submit_maintenance_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_submit_maintenance_non_technician(self):
        """Test that non-technician users cannot submit"""
        self.client.force_authenticate(user=self.host)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_submit_maintenance_device_not_assigned(self):
        """Test that technician cannot submit for unassigned device"""
        self.client.force_authenticate(user=self.other_technician)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not assigned to you', str(response.data))
    
    def test_submit_maintenance_duplicate_half_month(self):
        """Test that duplicate submissions for same half_month are rejected"""
        self.client.force_authenticate(user=self.technician)
        
        # Create first submission
        today = date.today()
        half_month = 1 if today.day <= 15 else 2
        
        Submission.objects.create(
            technician=self.technician,
            device=self.device,
            type='Cleaning',
            visit_date=today,
            half_month=half_month,
            status='Ok'
        )
        
        # Try to create duplicate
        data = {
            'device_id': self.device.id,
            'visit_date': today.isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already submitted', str(response.data))
    
    def test_submit_maintenance_invalid_device(self):
        """Test that submission fails for non-existent device"""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'device_id': 99999,  # Non-existent device
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_maintenance_invalid_status(self):
        """Test that invalid status values are rejected"""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Invalid Status',  # Invalid
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_maintenance_half_month_calculation(self):
        """Test that half_month is calculated correctly from visit_date"""
        self.client.force_authenticate(user=self.technician)
        
        # Test for first half of month (day 10)
        from datetime import datetime
        visit_date_half1 = date(2025, 10, 10)
        
        data = {
            'device_id': self.device.id,
            'visit_date': visit_date_half1.isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        submission = Submission.objects.get(device=self.device, technician=self.technician)
        self.assertEqual(submission.half_month, 1)
    
    def test_submit_maintenance_optional_remarks(self):
        """Test that remarks field is optional"""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            # No remarks field
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        submission = Submission.objects.get(device=self.device, technician=self.technician)
        self.assertEqual(submission.remarks, '')
    
    def test_submit_maintenance_response_includes_photos(self):
        """Test that response includes photo information"""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('photos', response.data['submission'])
        self.assertEqual(len(response.data['submission']['photos']), 8)
    
    def test_submit_maintenance_invalid_photo_format(self):
        """Test that invalid photo format is rejected"""
        self.client.force_authenticate(user=self.technician)
        
        # Create oversized photo to trigger validation error
        invalid_photos = self.photos.copy()
        oversized_photo = SimpleUploadedFile(
            "test.jpg",
            b"x" * (11 * 1024 * 1024),  # 11MB - over limit
            content_type="image/jpeg"
        )
        invalid_photos['section1_1'] = oversized_photo
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **invalid_photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        # Should fail due to oversized photo
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_maintenance_photo_sections(self):
        """Test that photos are saved with correct sections and order"""
        self.client.force_authenticate(user=self.technician)
        
        data = {
            'device_id': self.device.id,
            'visit_date': date.today().isoformat(),
            'job_description': 'Routine cleaning',
            'status': 'Ok',
            **self.photos
        }
        
        response = self.client.post('/api/technician/submit', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        submission = Submission.objects.get(device=self.device, technician=self.technician)
        
        # Verify section 1 has 3 photos
        section1_photos = Photo.objects.filter(submission=submission, section=1)
        self.assertEqual(section1_photos.count(), 3)
        
        # Verify section 2 has 3 photos
        section2_photos = Photo.objects.filter(submission=submission, section=2)
        self.assertEqual(section2_photos.count(), 3)
        
        # Verify section 3 has 2 photos
        section3_photos = Photo.objects.filter(submission=submission, section=3)
        self.assertEqual(section3_photos.count(), 2)
