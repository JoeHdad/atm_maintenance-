"""
Script to save SNB logo to the correct location
Run this script after placing your logo file in the same directory
"""

import os
import shutil
from pathlib import Path

def save_logo():
    """Save logo to media folder"""
    
    # Current directory
    current_dir = Path(__file__).parent
    
    # Target location
    media_dir = current_dir / 'media'
    target_path = media_dir / 'snb_logo.png'
    
    # Possible source locations
    possible_sources = [
        current_dir / 'snb_logo.png',  # Same directory as script
        current_dir.parent / 'snb_logo.png',  # Project root
        Path.home() / 'Downloads' / 'snb_logo.png',  # Downloads folder
    ]
    
    print("🔍 Searching for SNB logo...")
    print(f"Target location: {target_path}")
    print()
    
    # Find the logo
    source_path = None
    for path in possible_sources:
        if path.exists() and path.stat().st_size > 0:
            print(f"✅ Found logo at: {path}")
            print(f"   Size: {path.stat().st_size} bytes")
            source_path = path
            break
        else:
            print(f"❌ Not found or empty: {path}")
    
    if not source_path:
        print()
        print("⚠️  Logo file not found!")
        print()
        print("📋 Instructions:")
        print("1. Save your SNB logo as 'snb_logo.png'")
        print("2. Place it in one of these locations:")
        for path in possible_sources:
            print(f"   - {path.parent}")
        print("3. Run this script again")
        return False
    
    # Create media directory if it doesn't exist
    media_dir.mkdir(exist_ok=True)
    
    # Copy logo to target location
    try:
        # Remove old file if exists
        if target_path.exists():
            print(f"🗑️  Removing old file: {target_path}")
            target_path.unlink()
        
        # Copy new file
        print(f"📋 Copying logo to: {target_path}")
        shutil.copy2(source_path, target_path)
        
        # Verify
        if target_path.exists() and target_path.stat().st_size > 0:
            print()
            print("✅ SUCCESS! Logo saved successfully!")
            print(f"   Location: {target_path}")
            print(f"   Size: {target_path.stat().st_size} bytes")
            print()
            print("🎉 You can now generate PDFs with the logo!")
            return True
        else:
            print()
            print("❌ ERROR: Logo file is empty or not saved properly")
            return False
            
    except Exception as e:
        print()
        print(f"❌ ERROR: Failed to copy logo: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("SNB Logo Setup Script")
    print("=" * 60)
    print()
    
    success = save_logo()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Setup Complete!")
    else:
        print("❌ Setup Failed - Please follow the instructions above")
    print("=" * 60)
