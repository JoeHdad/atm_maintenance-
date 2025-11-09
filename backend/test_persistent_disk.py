#!/usr/bin/env python
"""
Test script to verify persistent disk functionality on Render.
This script should be run on the Render server to test file persistence.

Usage on Render:
1. SSH into Render container or use Render Shell
2. cd /opt/render/project/src/backend
3. python test_persistent_disk.py
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from django.conf import settings

print("\n" + "=" * 80)
print("PERSISTENT DISK TEST - RENDER PRODUCTION")
print("=" * 80)

# Test 1: Verify MEDIA_ROOT points to persistent disk
print("\n[TEST 1] MEDIA_ROOT Configuration:")
print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"  Type: {type(settings.MEDIA_ROOT)}")

if '/var/data' in str(settings.MEDIA_ROOT):
    print("  ✓ PASS: MEDIA_ROOT points to persistent disk")
else:
    print("  ✗ FAIL: MEDIA_ROOT does NOT point to persistent disk!")
    print("  ✗ Current path will NOT survive container restarts")
    sys.exit(1)

# Test 2: Check if persistent disk is mounted
print("\n[TEST 2] Persistent Disk Mount:")
persistent_disk = '/var/data'
if os.path.exists(persistent_disk):
    print(f"  ✓ PASS: {persistent_disk} exists")
    print(f"  Readable: {os.access(persistent_disk, os.R_OK)}")
    print(f"  Writable: {os.access(persistent_disk, os.W_OK)}")
else:
    print(f"  ✗ FAIL: {persistent_disk} does NOT exist!")
    print("  ✗ Persistent disk is not mounted")
    sys.exit(1)

# Test 3: Check MEDIA_ROOT directory
print("\n[TEST 3] MEDIA_ROOT Directory:")
if os.path.exists(settings.MEDIA_ROOT):
    print(f"  ✓ PASS: {settings.MEDIA_ROOT} exists")
    print(f"  Readable: {os.access(settings.MEDIA_ROOT, os.R_OK)}")
    print(f"  Writable: {os.access(settings.MEDIA_ROOT, os.W_OK)}")
else:
    print(f"  ✗ FAIL: {settings.MEDIA_ROOT} does NOT exist!")
    print("  Attempting to create...")
    try:
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        print(f"  ✓ Created: {settings.MEDIA_ROOT}")
    except Exception as e:
        print(f"  ✗ Failed to create: {e}")
        sys.exit(1)

# Test 4: Check subdirectories
print("\n[TEST 4] Subdirectories:")
subdirs = ['photos', 'pdfs', 'excel_uploads']
for subdir in subdirs:
    subdir_path = os.path.join(settings.MEDIA_ROOT, subdir)
    if os.path.exists(subdir_path):
        print(f"  ✓ {subdir}/: EXISTS")
    else:
        print(f"  ✗ {subdir}/: MISSING - Creating...")
        try:
            os.makedirs(subdir_path, exist_ok=True)
            print(f"    ✓ Created: {subdir_path}")
        except Exception as e:
            print(f"    ✗ Failed: {e}")

# Test 5: Write test file
print("\n[TEST 5] Write Test:")
test_file = os.path.join(settings.MEDIA_ROOT, f'test_persistence_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
test_content = f"Test file created at {datetime.now()}\nContainer ID: {os.environ.get('HOSTNAME', 'unknown')}\n"

try:
    with open(test_file, 'w') as f:
        f.write(test_content)
    print(f"  ✓ PASS: File written successfully")
    print(f"  Path: {test_file}")
    
    # Verify file exists
    if os.path.exists(test_file):
        print(f"  ✓ File verified to exist")
        file_size = os.path.getsize(test_file)
        print(f"  Size: {file_size} bytes")
    else:
        print(f"  ✗ FAIL: File does not exist after write!")
except Exception as e:
    print(f"  ✗ FAIL: Write failed: {e}")
    sys.exit(1)

# Test 6: List existing files
print("\n[TEST 6] Existing Files:")
photos_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
if os.path.exists(photos_dir):
    try:
        # Count total photos
        photo_count = 0
        submission_dirs = []
        for item in os.listdir(photos_dir):
            item_path = os.path.join(photos_dir, item)
            if os.path.isdir(item_path):
                submission_dirs.append(item)
                files_in_dir = [f for f in os.listdir(item_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
                photo_count += len(files_in_dir)
        
        print(f"  Submission directories: {len(submission_dirs)}")
        print(f"  Total photos: {photo_count}")
        
        if submission_dirs:
            print(f"  Sample directories: {submission_dirs[:5]}")
    except Exception as e:
        print(f"  Error scanning: {e}")
else:
    print(f"  Photos directory does not exist")

# Test 7: Environment variables
print("\n[TEST 7] Environment Variables:")
print(f"  MEDIA_ROOT env: {os.environ.get('MEDIA_ROOT', 'NOT SET')}")
print(f"  DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")
print(f"  HOSTNAME: {os.environ.get('HOSTNAME', 'NOT SET')}")

# Test 8: Container info
print("\n[TEST 8] Container Information:")
print(f"  Current working directory: {os.getcwd()}")
print(f"  Python executable: {sys.executable}")
print(f"  Django version: {django.get_version()}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nIMPORTANT NOTES:")
print("1. If MEDIA_ROOT points to /var/data/media - files will persist")
print("2. If MEDIA_ROOT points to /opt/render/... - files will be LOST on restart")
print("3. Keep the test file to verify persistence after container restart")
print("4. After container restarts, run this script again to check if test file still exists")
print("=" * 80 + "\n")
