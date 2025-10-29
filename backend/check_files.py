import os

upload_dir = 'media/excel_uploads'

if os.path.exists(upload_dir):
    files = os.listdir(upload_dir)
    print(f"✅ Upload directory exists: {upload_dir}")
    print(f"📁 Files found: {len(files)}")
    for f in files:
        file_path = os.path.join(upload_dir, f)
        size = os.path.getsize(file_path)
        print(f"   - {f} ({size} bytes)")
else:
    print(f"❌ Upload directory does not exist: {upload_dir}")
