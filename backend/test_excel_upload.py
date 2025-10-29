#!/usr/bin/env python
"""
Test script for Feature 2.3: Excel Upload & Parse
Tests the Excel parser and upload functionality
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import User, Device, TechnicianDevice
from core.utils.excel_parser import ExcelParser, ExcelParserError, parse_excel_file
from openpyxl import Workbook
from io import BytesIO

def create_test_excel():
    """Create a test Excel file in memory"""
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    ws.append(['Interaction ID', 'Gfm cost Center', 'Status', 'Gfm Problem Type', 'Gfm Problem Date'])
    
    # Add test data
    test_data = [
        ['ATM-TEST-001', 'CC-10001', 'Central Region', 'Cleaning Required', '2025-01-15'],
        ['ATM-TEST-002', 'CC-10002', 'North Region', 'Maintenance Due', '2025-01-16'],
        ['ATM-TEST-003', 'CC-10003', 'South Region', 'Inspection Needed', '2025-01-17'],
        ['ATM-TEST-004', 'CC-10004', 'East Region', 'Repair Required', '2025-01-18'],
        ['ATM-TEST-005', 'CC-10005', 'West Region', 'Cleaning Required', '2025-01-19'],
    ]
    
    for row in test_data:
        ws.append(row)
    
    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return excel_file

def test_excel_parser():
    """Test the Excel parser functionality"""
    print("\n" + "="*60)
    print("TEST 1: Excel Parser Functionality")
    print("="*60)
    
    try:
        # Create test Excel file
        excel_file = create_test_excel()
        
        # Test parsing
        print("\n✓ Creating test Excel file...")
        parsed_data, row_count = parse_excel_file(excel_file, 'test_devices.xlsx')
        
        print(f"✓ Successfully parsed {row_count} rows")
        print(f"\nParsed data sample:")
        for i, device in enumerate(parsed_data[:3], 1):
            print(f"  {i}. {device['interaction_id']} - {device['region']} - {device['gfm_problem_date']}")
        
        # Validate data structure
        assert row_count == 5, f"Expected 5 rows, got {row_count}"
        assert all('interaction_id' in d for d in parsed_data), "Missing interaction_id"
        assert all('gfm_cost_center' in d for d in parsed_data), "Missing gfm_cost_center"
        assert all('region' in d for d in parsed_data), "Missing region"
        assert all('gfm_problem_type' in d for d in parsed_data), "Missing gfm_problem_type"
        assert all('gfm_problem_date' in d for d in parsed_data), "Missing gfm_problem_date"
        
        print("\n✓ All data structure validations passed")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """Test database operations (create technician and devices)"""
    print("\n" + "="*60)
    print("TEST 2: Database Operations")
    print("="*60)
    
    try:
        # Create test technician
        print("\n✓ Creating test technician...")
        technician, created = User.objects.get_or_create(
            username='test_tech_excel',
            defaults={
                'role': 'technician',
                'city': 'Riyadh'
            }
        )
        
        if created:
            technician.set_password('testpass123')
            technician.save()
            print(f"  Created new technician: {technician.username}")
        else:
            print(f"  Using existing technician: {technician.username}")
        
        # Delete existing devices for this technician
        print("\n✓ Cleaning up existing devices...")
        existing_count = TechnicianDevice.objects.filter(technician=technician).count()
        if existing_count > 0:
            TechnicianDevice.objects.filter(technician=technician).delete()
            print(f"  Deleted {existing_count} existing device assignments")
        
        # Create test Excel file and parse
        print("\n✓ Parsing Excel file...")
        excel_file = create_test_excel()
        parsed_data, row_count = parse_excel_file(excel_file, 'test_devices.xlsx')
        
        # Create devices
        print(f"\n✓ Creating {row_count} devices...")
        created_devices = []
        for device_data in parsed_data:
            device = Device.objects.create(
                interaction_id=device_data['interaction_id'],
                gfm_cost_center=device_data['gfm_cost_center'],
                region=device_data['region'],
                gfm_problem_type=device_data['gfm_problem_type'],
                gfm_problem_date=device_data['gfm_problem_date'],
                city=technician.city,
                type='Cleaning'
            )
            created_devices.append(device)
        
        print(f"  Created {len(created_devices)} devices")
        
        # Create assignments
        print("\n✓ Creating device assignments...")
        assignments = [
            TechnicianDevice(technician=technician, device=device)
            for device in created_devices
        ]
        TechnicianDevice.objects.bulk_create(assignments)
        print(f"  Created {len(assignments)} assignments")
        
        # Verify
        print("\n✓ Verifying database records...")
        device_count = Device.objects.filter(
            interaction_id__startswith='ATM-TEST-'
        ).count()
        assignment_count = TechnicianDevice.objects.filter(
            technician=technician
        ).count()
        
        print(f"  Devices in database: {device_count}")
        print(f"  Assignments in database: {assignment_count}")
        
        assert device_count == 5, f"Expected 5 devices, found {device_count}"
        assert assignment_count == 5, f"Expected 5 assignments, found {assignment_count}"
        
        print("\n✓ All database operations successful")
        return True, technician
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_replace_strategy(technician):
    """Test the REPLACE strategy (delete old, create new)"""
    print("\n" + "="*60)
    print("TEST 3: REPLACE Strategy")
    print("="*60)
    
    try:
        # Check current count
        print("\n✓ Checking current device count...")
        initial_count = TechnicianDevice.objects.filter(technician=technician).count()
        print(f"  Initial device count: {initial_count}")
        
        # Delete existing devices (REPLACE strategy)
        print("\n✓ Deleting existing devices...")
        existing_assignments = TechnicianDevice.objects.filter(
            technician=technician
        ).select_related('device')
        
        existing_device_ids = [a.device.id for a in existing_assignments]
        TechnicianDevice.objects.filter(technician=technician).delete()
        Device.objects.filter(id__in=existing_device_ids).delete()
        
        after_delete_count = TechnicianDevice.objects.filter(technician=technician).count()
        print(f"  Device count after delete: {after_delete_count}")
        
        assert after_delete_count == 0, "Devices not properly deleted"
        
        # Create new devices
        print("\n✓ Creating new set of devices...")
        excel_file = create_test_excel()
        parsed_data, row_count = parse_excel_file(excel_file, 'test_devices.xlsx')
        
        created_devices = []
        for device_data in parsed_data:
            device = Device.objects.create(
                interaction_id=device_data['interaction_id'],
                gfm_cost_center=device_data['gfm_cost_center'],
                region=device_data['region'],
                gfm_problem_type=device_data['gfm_problem_type'],
                gfm_problem_date=device_data['gfm_problem_date'],
                city=technician.city,
                type='Electrical'  # Different type this time
            )
            created_devices.append(device)
        
        assignments = [
            TechnicianDevice(technician=technician, device=device)
            for device in created_devices
        ]
        TechnicianDevice.objects.bulk_create(assignments)
        
        final_count = TechnicianDevice.objects.filter(technician=technician).count()
        print(f"  Final device count: {final_count}")
        
        # Verify all devices are new (type='Electrical')
        electrical_count = Device.objects.filter(
            assigned_technicians__technician=technician,
            type='Electrical'
        ).count()
        
        print(f"  Electrical devices: {electrical_count}")
        
        assert final_count == 5, f"Expected 5 devices, found {final_count}"
        assert electrical_count == 5, "REPLACE strategy failed - old devices still exist"
        
        print("\n✓ REPLACE strategy working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """Clean up test data"""
    print("\n" + "="*60)
    print("CLEANUP: Removing Test Data")
    print("="*60)
    
    try:
        # Delete test devices
        deleted_devices = Device.objects.filter(
            interaction_id__startswith='ATM-TEST-'
        ).delete()
        print(f"\n✓ Deleted test devices: {deleted_devices[0]} records")
        
        # Delete test technician
        deleted_users = User.objects.filter(
            username='test_tech_excel'
        ).delete()
        print(f"✓ Deleted test technician: {deleted_users[0]} records")
        
        print("\n✓ Cleanup complete")
        
    except Exception as e:
        print(f"\n✗ Cleanup failed: {e}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FEATURE 2.3: EXCEL UPLOAD & PARSE - TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Excel Parser
    results.append(("Excel Parser", test_excel_parser()))
    
    # Test 2: Database Operations
    db_result, technician = test_database_operations()
    results.append(("Database Operations", db_result))
    
    # Test 3: REPLACE Strategy
    if technician:
        results.append(("REPLACE Strategy", test_replace_strategy(technician)))
    
    # Cleanup
    cleanup()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return all(passed for _, passed in results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
