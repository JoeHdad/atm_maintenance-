"""
File handling utilities for photo uploads and validation.
"""

import os
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError


class FileHandlerError(Exception):
    """Custom exception for file handling errors"""
    pass


def validate_photo_format(file):
    """
    Validate that the uploaded file is a valid image format.
    
    Args:
        file: UploadedFile object
        
    Returns:
        bool: True if valid
        
    Raises:
        FileHandlerError: If file format is invalid
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    file_name = file.name.lower()
    
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        raise FileHandlerError(
            f"Invalid file format. Allowed formats: {', '.join(allowed_extensions)}"
        )
    
    return True


def validate_photo_size(file, max_size_mb=10):
    """
    Validate that the uploaded file size is within limits.
    
    Args:
        file: UploadedFile object
        max_size_mb: Maximum file size in megabytes
        
    Returns:
        bool: True if valid
        
    Raises:
        FileHandlerError: If file size exceeds limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise FileHandlerError(
            f"File size exceeds {max_size_mb}MB limit. File size: {file.size / (1024 * 1024):.2f}MB"
        )
    
    return True


def validate_photo(file):
    """
    Validate photo format and size.
    
    Args:
        file: UploadedFile object
        
    Returns:
        bool: True if valid
        
    Raises:
        FileHandlerError: If validation fails
    """
    validate_photo_format(file)
    validate_photo_size(file)
    return True


def save_photo(file, submission_id, section, order_index):
    """
    Save uploaded photo to disk with organized directory structure.
    
    Args:
        file: UploadedFile object
        submission_id: ID of the submission
        section: Photo section (1-5)
        order_index: Photo order within section
        
    Returns:
        str: Relative path to saved file
        
    Raises:
        FileHandlerError: If save operation fails
    """
    try:
        # Validate photo first
        validate_photo(file)
        
        # Create directory structure: /media/photos/{submission_id}/
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'photos', str(submission_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename with section and order
        file_extension = os.path.splitext(file.name)[1].lower()
        unique_filename = f"section{section}_{order_index}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file to disk
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Return relative path for database storage
        relative_path = os.path.join('photos', str(submission_id), unique_filename)
        return relative_path
        
    except Exception as e:
        raise FileHandlerError(f"Failed to save photo: {str(e)}")


def save_submission_photos(files_dict, submission_id, is_electrical=False):
    """
    Save all photos for a submission (8 for default, 19 for electrical).
    
    Args:
        files_dict: Dictionary with photo files
        submission_id: ID of the submission
        is_electrical: Boolean indicating if this is an electrical device submission
        
    Returns:
        list: List of dictionaries with photo info (section, order_index, file_path)
        
    Raises:
        FileHandlerError: If any photo save fails
    """
    if is_electrical:
        # Electrical: 5 sections (4+4+4+4+3 = 19 photos)
        photo_mapping = [
            # Section 1: 4 photos
            ('section1_1', 1, 1),
            ('section1_2', 1, 2),
            ('section1_3', 1, 3),
            ('section1_4', 1, 4),
            # Section 2: 4 photos
            ('section2_1', 2, 1),
            ('section2_2', 2, 2),
            ('section2_3', 2, 3),
            ('section2_4', 2, 4),
            # Section 3: 4 photos
            ('section3_1', 3, 1),
            ('section3_2', 3, 2),
            ('section3_3', 3, 3),
            ('section3_4', 3, 4),
            # Section 4: 4 photos
            ('section4_1', 4, 1),
            ('section4_2', 4, 2),
            ('section4_3', 4, 3),
            ('section4_4', 4, 4),
            # Section 5: 3 photos
            ('section5_1', 5, 1),
            ('section5_2', 5, 2),
            ('section5_3', 5, 3),
        ]
    else:
        # Default: 3 sections (3+3+2 = 8 photos)
        photo_mapping = [
            ('section1_1', 1, 1),
            ('section1_2', 1, 2),
            ('section1_3', 1, 3),
            ('section2_1', 2, 1),
            ('section2_2', 2, 2),
            ('section2_3', 2, 3),
            ('section3_1', 3, 1),
            ('section3_2', 3, 2),
        ]
    
    saved_photos = []
    
    for field_name, section, order_index in photo_mapping:
        if field_name not in files_dict:
            raise FileHandlerError(f"Missing required photo: {field_name}")
        
        file = files_dict[field_name]
        file_path = save_photo(file, submission_id, section, order_index)
        
        saved_photos.append({
            'section': section,
            'order_index': order_index,
            'file_path': file_path
        })
    
    return saved_photos


def delete_submission_photos(submission_id):
    """
    Delete all photos for a submission from disk.
    
    Args:
        submission_id: ID of the submission
        
    Returns:
        bool: True if successful
    """
    try:
        photo_dir = os.path.join(settings.MEDIA_ROOT, 'photos', str(submission_id))
        
        if os.path.exists(photo_dir):
            import shutil
            shutil.rmtree(photo_dir)
        
        return True
    except Exception as e:
        print(f"Error deleting photos for submission {submission_id}: {str(e)}")
        return False
