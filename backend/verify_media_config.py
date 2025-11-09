#!/usr/bin/env python
"""
Diagnostic script to verify MEDIA_ROOT configuration and persistent disk setup.
Run this on Render to verify the media storage configuration.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from django.conf import settings

print("=" * 80)
print("MEDIA CONFIGURATION DIAGNOSTIC REPORT")
print("=" * 80)

# 1. MEDIA_ROOT Configuration
print("\n[1] MEDIA_ROOT CONFIGURATION:")
print(f"    Value: {settings.MEDIA_ROOT}")
print(f"    Type: {type(settings.MEDIA_ROOT)}")
print(f"    Is String: {isinstance(settings.MEDIA_ROOT, str)}")

# 2. Environment Variable Check
print("\n[2] ENVIRONMENT VARIABLE:")
env_media_root = os.environ.get('MEDIA_ROOT', 'NOT SET')
print(f"    MEDIA_ROOT env var: {env_media_root}")
print(f"    Matches settings: {env_media_root == str(settings.MEDIA_ROOT)}")

# 3. Path Existence Check
print("\n[3] PATH EXISTENCE:")
print(f"    MEDIA_ROOT exists: {os.path.exists(settings.MEDIA_ROOT)}")
print(f"    Is directory: {os.path.isdir(settings.MEDIA_ROOT)}")

if os.path.exists(settings.MEDIA_ROOT):
    print(f"    Absolute path: {os.path.abspath(settings.MEDIA_ROOT)}")
    
    # Check permissions
    print(f"    Readable: {os.access(settings.MEDIA_ROOT, os.R_OK)}")
    print(f"    Writable: {os.access(settings.MEDIA_ROOT, os.W_OK)}")
    print(f"    Executable: {os.access(settings.MEDIA_ROOT, os.X_OK)}")

# 4. Subdirectories Check
print("\n[4] SUBDIRECTORIES:")
subdirs = ['photos', 'pdfs', 'excel_uploads']
for subdir in subdirs:
    subdir_path = os.path.join(settings.MEDIA_ROOT, subdir)
    exists = os.path.exists(subdir_path)
    print(f"    {subdir}/: {'✓ EXISTS' if exists else '✗ MISSING'}")
    if exists:
        print(f"        Path: {subdir_path}")
        print(f"        Writable: {os.access(subdir_path, os.W_OK)}")
        # List files if any
        try:
            files = os.listdir(subdir_path)
            print(f"        Files/Dirs: {len(files)}")
            if files:
                print(f"        Sample: {files[:3]}")
        except Exception as e:
            print(f"        Error listing: {e}")

# 5. Disk Space Check
print("\n[5] DISK SPACE:")
if os.path.exists(settings.MEDIA_ROOT):
    try:
        stat = os.statvfs(settings.MEDIA_ROOT)
        total_space = stat.f_blocks * stat.f_frsize
        free_space = stat.f_bavail * stat.f_frsize
        used_space = total_space - free_space
        
        print(f"    Total: {total_space / (1024**3):.2f} GB")
        print(f"    Used: {used_space / (1024**3):.2f} GB")
        print(f"    Free: {free_space / (1024**3):.2f} GB")
        print(f"    Usage: {(used_space / total_space * 100):.1f}%")
    except Exception as e:
        print(f"    Unable to check disk space: {e}")

# 6. Recent Files Check
print("\n[6] RECENT UPLOADED FILES:")
photos_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
if os.path.exists(photos_dir):
    try:
        # Find all photo files
        photo_files = []
        for root, dirs, files in os.walk(photos_dir):
            for file in files:
                if file.endswith(('.jpg', '.jpeg', '.png')):
                    full_path = os.path.join(root, file)
                    stat_info = os.stat(full_path)
                    photo_files.append({
                        'path': full_path,
                        'size': stat_info.st_size,
                        'mtime': stat_info.st_mtime
                    })
        
        # Sort by modification time (newest first)
        photo_files.sort(key=lambda x: x['mtime'], reverse=True)
        
        print(f"    Total photos found: {len(photo_files)}")
        if photo_files:
            print(f"    Recent files (last 5):")
            for i, photo in enumerate(photo_files[:5], 1):
                from datetime import datetime
                mtime = datetime.fromtimestamp(photo['mtime'])
                print(f"        {i}. {photo['path']}")
                print(f"           Size: {photo['size']} bytes, Modified: {mtime}")
        else:
            print("    No photos found")
    except Exception as e:
        print(f"    Error scanning photos: {e}")
else:
    print("    Photos directory does not exist!")

# 7. Test Write Operation
print("\n[7] WRITE TEST:")
test_file = os.path.join(settings.MEDIA_ROOT, 'test_write.txt')
try:
    with open(test_file, 'w') as f:
        f.write('Test write operation')
    print(f"    ✓ Write successful: {test_file}")
    
    # Verify file exists
    if os.path.exists(test_file):
        print(f"    ✓ File verified to exist")
        # Clean up
        os.remove(test_file)
        print(f"    ✓ Test file removed")
    else:
        print(f"    ✗ File does not exist after write!")
except Exception as e:
    print(f"    ✗ Write failed: {e}")

# 8. Django Media URL Configuration
print("\n[8] MEDIA URL CONFIGURATION:")
print(f"    MEDIA_URL: {settings.MEDIA_URL}")
print(f"    MEDIA_BASE_URL: {getattr(settings, 'MEDIA_BASE_URL', 'NOT SET')}")

# 9. Persistent Disk Detection
print("\n[9] PERSISTENT DISK DETECTION:")
media_root_str = str(settings.MEDIA_ROOT)
if '/var/data' in media_root_str:
    print("    ✓ MEDIA_ROOT points to persistent disk (/var/data)")
    print("    ✓ Files should survive container restarts")
elif '/opt/render/project' in media_root_str:
    print("    ✗ WARNING: MEDIA_ROOT points to ephemeral storage!")
    print("    ✗ Files will be LOST on container restart!")
    print("    ✗ ACTION REQUIRED: Set MEDIA_ROOT=/var/data/media")
else:
    print(f"    ? Unknown storage location: {media_root_str}")
    print("    ? Verify if this is persistent or ephemeral")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
