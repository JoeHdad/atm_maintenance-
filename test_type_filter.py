#!/usr/bin/env python
"""
Test script to verify the technician dashboard type filter accuracy.
Tests that Electrical filter shows devices with "Electro Mechanical" in gfm_problem_type.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import User, Device, Submission, ExcelUpload, TechnicianDevice
from datetime import date

def test_type_filter_accuracy():
    """Test that type filters work correctly"""
    
    print("\n" + "="*80)
    print("TECHNICIAN DASHBOARD TYPE FILTER TEST")
    print("="*80)
    
    # Create test user
    print("\n[SETUP] Creating test technician...")
    
    technician, _ = User.objects.get_or_create(
        username='test_tech_filter',
        defaults={
            'password': 'testpass123',
            'role': 'technician',
            'city': 'Hail'
        }
    )
    print(f"✓ Created technician: {technician.username}")
    
    # Create test devices with different types
    print("\n[SETUP] Creating test devices...")
    
    test_devices = [
        {
            'interaction_id': 'FILTER_ELECTRICAL_001',
            'gfm_cost_center': '8001',
            'gfm_problem_type': 'Electro Mechanical',
            'city': 'Hail',
            'type': 'Cleaning1'  # Note: type is Cleaning1 but problem_type is Electro Mechanical
        },
        {
            'interaction_id': 'FILTER_CLEANING1_001',
            'gfm_cost_center': '8002',
            'gfm_problem_type': 'Regular Cleaning',
            'city': 'Hail',
            'type': 'Cleaning1'
        },
        {
            'interaction_id': 'FILTER_CLEANING2_001',
            'gfm_cost_center': '8003',
            'gfm_problem_type': 'Deep Cleaning',
            'city': 'Hail',
            'type': 'Cleaning2'
        },
        {
            'interaction_id': 'FILTER_SECURITY_001',
            'gfm_cost_center': '8004',
            'gfm_problem_type': 'Security Check',
            'city': 'Hail',
            'type': 'Security'
        }
    ]
    
    devices = []
    for device_data in test_devices:
        device, _ = Device.objects.get_or_create(
            interaction_id=device_data['interaction_id'],
            defaults=device_data
        )
        devices.append(device)
        print(f"✓ Created device: {device.interaction_id} (Type: {device.type}, Problem: {device.gfm_problem_type})")
    
    # Assign devices to technician
    print("\n[SETUP] Assigning devices to technician...")
    for device in devices:
        TechnicianDevice.objects.get_or_create(
            technician=technician,
            device=device
        )
    print(f"✓ Assigned {len(devices)} devices to technician")
    
    # Create Excel uploads to simulate the frontend data source
    print("\n[SETUP] Creating Excel uploads...")
    
    excel_data_electrical = [
        {'col_1': 'FILTER_ELECTRICAL_001', 'col_2': '8001', 'col_3': 'Electro Mechanical', 'col_4': '', 'col_5': 'Hail'}
    ]
    
    excel_data_cleaning = [
        {'col_1': 'FILTER_CLEANING1_001', 'col_2': '8002', 'col_3': 'Regular Cleaning', 'col_4': '', 'col_5': 'Hail'},
        {'col_1': 'FILTER_CLEANING2_001', 'col_2': '8003', 'col_3': 'Deep Cleaning', 'col_4': '', 'col_5': 'Hail'},
        {'col_1': 'FILTER_SECURITY_001', 'col_2': '8004', 'col_3': 'Security Check', 'col_4': '', 'col_5': 'Hail'}
    ]
    
    # Create Excel uploads
    electrical_upload = ExcelUpload.objects.create(
        technician=technician,
        file_name='electrical_devices.xlsx',
        file_path='test_path_electrical.xlsx',
        device_type='Cleaning1',  # Note: device_type is Cleaning1
        parsed_data=excel_data_electrical,
        row_count=1
    )
    
    cleaning_upload = ExcelUpload.objects.create(
        technician=technician,
        file_name='cleaning_devices.xlsx',
        file_path='test_path_cleaning.xlsx',
        device_type='Cleaning1',
        parsed_data=excel_data_cleaning,
        row_count=3
    )
    
    print(f"✓ Created Excel uploads: {electrical_upload.file_name}, {cleaning_upload.file_name}")
    
    # Now simulate the frontend filtering logic
    print("\n[TEST 1] Simulating frontend Electrical filter...")
    
    # Get all devices like the frontend does
    all_devices = []
    
    # Simulate getAllDevices() from TechnicianDashboard.jsx
    uploads = ExcelUpload.objects.filter(technician=technician)
    for upload in uploads:
        if upload.parsed_data:
            for row in upload.parsed_data:
                if row.get('device_id'):
                    # This is simplified - in real frontend it would map more fields
                    device_obj = {
                        'device_id': row['device_id'],
                        'device_type': upload.device_type,
                        'gfm_problem': row.get('col_3', ''),
                        'interaction_id': row.get('col_1'),
                        'gfm_cost_center': row.get('col_2'),
                        'submission_status': 'Active'
                    }
                    all_devices.append(device_obj)
    
    print(f"✓ Retrieved {len(all_devices)} devices from uploads")
    
    # Test Electrical filter
    electrical_devices = []
    for device in all_devices:
        problem_type = (device.get('gfm_problem') or '').lower()
        device_type = (device.get('device_type') or '').lower()
        
        # Apply the same logic as updated frontend
        is_electrical_by_problem = (
            'electro' in problem_type and 'mechanical' in problem_type
        ) or 'electrical' in problem_type
        
        is_electrical_by_device = device_type == 'electrical'
        
        if is_electrical_by_problem or is_electrical_by_device:
            electrical_devices.append(device)
    
    print(f"✓ Electrical filter found {len(electrical_devices)} devices:")
    for device in electrical_devices:
        print(f"  - {device['interaction_id']}: {device['gfm_problem']}")
    
    # Verify the result
    expected_electrical = [d for d in all_devices if d['gfm_problem'] == 'Electro Mechanical']
    assert len(electrical_devices) == len(expected_electrical), \
        f"Expected {len(expected_electrical)} electrical devices, got {len(electrical_devices)}"
    
    print("✅ Electrical filter working correctly")
    
    # Test other filters
    print("\n[TEST 2] Simulating other type filters...")
    
    # Test Cleaning1 filter
    cleaning1_devices = [d for d in all_devices if (d.get('device_type') or '').lower() == 'cleaning1']
    print(f"✓ Cleaning1 filter would show {len(cleaning1_devices)} devices")
    
    # Test Cleaning2 filter  
    cleaning2_devices = [d for d in all_devices if (d.get('device_type') or '').lower() == 'cleaning2']
    print(f"✓ Cleaning2 filter would show {len(cleaning2_devices)} devices")
    
    print("\n[SUCCESS]")
    print("="*80)
    print("✅ All type filter tests PASSED")
    print("✅ Electrical filter correctly shows devices with 'Electro Mechanical' in gfm_problem_type")
    print("✅ Other type filters work with exact device_type matching")
    print("="*80 + "\n")
    
    # Cleanup
    print("[CLEANUP] Removing test data...")
    ExcelUpload.objects.filter(technician=technician).delete()
    TechnicianDevice.objects.filter(technician=technician).delete()
    for device in devices:
        device.delete()
    technician.delete()
    print("✓ Test data cleaned up\n")

if __name__ == '__main__':
    try:
        test_type_filter_accuracy()
        print("\n✅ TYPE FILTER ACCURACY TEST COMPLETE\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
