#!/usr/bin/env python
"""
Debug script to check ExcelUpload records in the database.
Run this from the backend directory: python debug_excel_uploads.py
"""
import os
import sys
import django

# Setup Django environment
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import ExcelUpload, User

def main():
    print("=" * 80)
    print("EXCEL UPLOAD DEBUG REPORT")
    print("=" * 80)
    
    # Get all technicians
    technicians = User.objects.filter(role='technician')
    print(f"\nTotal Technicians: {technicians.count()}")
    
    for tech in technicians:
        print(f"\n{'=' * 80}")
        print(f"Technician: {tech.username} (ID: {tech.id})")
        print(f"{'=' * 80}")
        
        # Get all uploads for this technician
        uploads = ExcelUpload.objects.filter(technician=tech).order_by('-upload_date')
        print(f"Total Uploads: {uploads.count()}")
        
        if uploads.exists():
            print("\nUpload Details:")
            print("-" * 80)
            for upload in uploads:
                print(f"  Upload ID: {upload.id}")
                print(f"  Device Type: {upload.device_type}")
                print(f"  File Name: {upload.file_name}")
                print(f"  Row Count: {upload.row_count}")
                print(f"  Upload Date: {upload.upload_date}")
                print(f"  Data Preview: {len(upload.parsed_data)} rows")
                if upload.parsed_data:
                    print(f"  First Row Keys: {list(upload.parsed_data[0].keys()) if upload.parsed_data else 'N/A'}")
                print("-" * 80)
        else:
            print("  No uploads found for this technician.")
    
    # Summary by device type
    print(f"\n{'=' * 80}")
    print("SUMMARY BY DEVICE TYPE")
    print(f"{'=' * 80}")
    
    all_uploads = ExcelUpload.objects.all()
    device_types = all_uploads.values_list('device_type', flat=True).distinct()
    
    for device_type in device_types:
        count = all_uploads.filter(device_type=device_type).count()
        print(f"  {device_type}: {count} upload(s)")
    
    print(f"\n{'=' * 80}")
    print("END OF REPORT")
    print(f"{'=' * 80}\n")

if __name__ == '__main__':
    main()
