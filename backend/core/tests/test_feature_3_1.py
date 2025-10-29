"""
Unit and Integration Tests for Feature 3.1: Device List View (Backend)
Tests the GET /api/technician/devices endpoint
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from core.models import Device, TechnicianDevice, Submission

User = get_user_model()


class TechnicianDevicesViewTest(TestCase):
    """Test cases for technician devices list endpoint"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.technician1 = User.objects.create_user(
            username='tech1',
            password='testpass123',
            role='technician',
            city='Riyadh'
        )
        
        self.technician2 = User.objects.create_user(
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
        
        # Create devices
        self.device1 = Device.objects.create(
            interaction_id='ATM001',
            gfm_cost_center='CC001',
            region='Central',
            gfm_problem_type='Hardware',
            gfm_problem_date=date.today() - timedelta(days=5),
            city='Riyadh',
            type='Cleaning'
        )
        
        self.device2 = Device.objects.create(
            interaction_id='ATM002',
            gfm_cost_center='CC002',
            region='North',
            gfm_problem_type='Software',
            gfm_problem_date=date.today() - timedelta(days=3),
            city='Riyadh',
            type='Electrical'
        )
        
        self.device3 = Device.objects.create(
            interaction_id='ATM003',
            gfm_cost_center='CC003',
            region='West',
            gfm_problem_type='Network',
            gfm_problem_date=date.today() - timedelta(days=1),
            city='Jeddah',
            type='Cleaning'
        )
        
        # Assign devices to technician1
        TechnicianDevice.objects.create(technician=self.technician1, device=self.device1)
        TechnicianDevice.objects.create(technician=self.technician1, device=self.device2)
        
        # Assign device3 to technician2
        TechnicianDevice.objects.create(technician=self.technician2, device=self.device3)
        
        # API client
        self.client = APIClient()
    
    def test_technician_can_access_devices(self):
        """Test that technician can access their assigned devices"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('devices', response.data)
        self.assertEqual(response.data['count'], 2)
    
    def test_non_technician_cannot_access(self):
        """Test that non-technician users get 403"""
        self.client.force_authenticate(user=self.host)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_cannot_access(self):
        """Test that unauthenticated requests get 401"""
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_filter_by_type_cleaning(self):
        """Test filtering devices by Cleaning type"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices?type=Cleaning')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['devices'][0]['type'], 'Cleaning')
    
    def test_filter_by_type_electrical(self):
        """Test filtering devices by Electrical type"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices?type=Electrical')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['devices'][0]['type'], 'Electrical')
    
    def test_filter_by_status(self):
        """Test filtering devices by status (region)"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices?status=Central')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['devices'][0]['region'], 'Central')
    
    def test_devices_ordered_by_problem_date(self):
        """Test that devices are ordered by problem date descending"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        devices = response.data['devices']
        
        # device2 has more recent problem date than device1
        self.assertEqual(devices[0]['interaction_id'], 'ATM002')
        self.assertEqual(devices[1]['interaction_id'], 'ATM001')
    
    def test_submission_status_pending(self):
        """Test submission status is 'pending' when no submission exists"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for device in response.data['devices']:
            self.assertEqual(device['submission_status'], 'pending')
    
    def test_submission_status_submitted(self):
        """Test submission status is 'submitted' when submission exists for current half_month"""
        # Create submission for device1 for current half_month
        today = date.today()
        current_half_month = 1 if today.day <= 15 else 2
        
        Submission.objects.create(
            technician=self.technician1,
            device=self.device1,
            type='Cleaning',
            visit_date=today,
            half_month=current_half_month,
            status='Pending'
        )
        
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find device1 in response
        device1_data = next(d for d in response.data['devices'] if d['id'] == self.device1.id)
        self.assertEqual(device1_data['submission_status'], 'submitted')
    
    def test_next_due_date_exists(self):
        """Test that next_due_date field is present in response"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for device in response.data['devices']:
            self.assertIn('next_due_date', device)
            self.assertIsNotNone(device['next_due_date'])
    
    def test_technician_only_sees_own_devices(self):
        """Test that technician only sees devices assigned to them"""
        self.client.force_authenticate(user=self.technician2)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['devices'][0]['interaction_id'], 'ATM003')
    
    def test_technician_only_sees_devices_in_their_city(self):
        """Test that technician only sees devices in their assigned city"""
        # Assign a device from different city to technician1
        device_other_city = Device.objects.create(
            interaction_id='ATM004',
            gfm_cost_center='CC004',
            region='South',
            gfm_problem_type='Hardware',
            gfm_problem_date=date.today(),
            city='Dammam',  # Different city
            type='Cleaning'
        )
        TechnicianDevice.objects.create(technician=self.technician1, device=device_other_city)
        
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should still only see 2 devices (from Riyadh)
        self.assertEqual(response.data['count'], 2)
        
        # Verify no device from Dammam
        device_ids = [d['interaction_id'] for d in response.data['devices']]
        self.assertNotIn('ATM004', device_ids)
    
    def test_empty_result_when_no_devices(self):
        """Test that empty list is returned when technician has no devices"""
        # Create new technician with no devices
        tech_no_devices = User.objects.create_user(
            username='tech_empty',
            password='testpass123',
            role='technician',
            city='Mecca'
        )
        
        self.client.force_authenticate(user=tech_no_devices)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['devices']), 0)
    
    def test_response_includes_all_device_fields(self):
        """Test that response includes all required device fields"""
        self.client.force_authenticate(user=self.technician1)
        response = self.client.get('/api/technician/devices')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        device = response.data['devices'][0]
        
        # Check all required fields
        required_fields = [
            'id', 'interaction_id', 'gfm_cost_center', 'region',
            'gfm_problem_type', 'gfm_problem_date', 'city', 'type',
            'submission_status', 'next_due_date', 'created_at'
        ]
        
        for field in required_fields:
            self.assertIn(field, device)
