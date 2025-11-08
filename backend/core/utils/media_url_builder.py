"""
Utility module for building absolute URLs for media files.
Handles cross-domain media file serving between Render backend and Hostinger frontend.
"""
from django.conf import settings
from urllib.parse import urljoin


def get_media_base_url(request=None):
    """
    Get the base URL for media files.
    
    In production:
    - Backend is on Render: https://atm-maintenance.onrender.com
    - Frontend is on Hostinger: https://amanisafi.com
    - Media files are served from Render backend
    
    Args:
        request: Optional Django request object
        
    Returns:
        str: Base URL for media files (e.g., https://atm-maintenance.onrender.com)
    """
    # Try to get from settings first (for explicit configuration)
    media_base_url = getattr(settings, 'MEDIA_BASE_URL', None)
    
    if media_base_url:
        return media_base_url.rstrip('/')
    
    # Fallback: construct from request if available
    if request:
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return f"{scheme}://{host}"
    
    # Final fallback: use ALLOWED_HOSTS or default
    if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
        host = settings.ALLOWED_HOSTS[0]
        # Determine scheme based on DEBUG setting
        scheme = 'http' if settings.DEBUG else 'https'
        return f"{scheme}://{host}"
    
    # Last resort
    return 'https://atm-maintenance.onrender.com'


def build_absolute_media_url(relative_path, request=None):
    """
    Build an absolute URL for a media file.
    
    Args:
        relative_path: Relative path to media file (e.g., 'photos/123/image.jpg')
        request: Optional Django request object for context
        
    Returns:
        str: Absolute URL (e.g., https://atm-maintenance.onrender.com/media/photos/123/image.jpg)
    """
    if not relative_path:
        return None
    
    # Normalize path separators (convert backslashes to forward slashes)
    normalized_path = str(relative_path).replace('\\', '/')
    
    # Get base URL
    base_url = get_media_base_url(request)
    
    # Construct full URL
    media_url = settings.MEDIA_URL.rstrip('/')
    full_url = f"{base_url}{media_url}/{normalized_path}"
    
    return full_url


def build_absolute_pdf_url(relative_path, request=None):
    """
    Build an absolute URL for a PDF file.
    
    Args:
        relative_path: Relative path to PDF file (e.g., 'pdfs/123/report.pdf')
        request: Optional Django request object for context
        
    Returns:
        str: Absolute URL (e.g., https://atm-maintenance.onrender.com/media/pdfs/123/report.pdf)
    """
    return build_absolute_media_url(relative_path, request)


def is_absolute_url(url):
    """
    Check if a URL is already absolute.
    
    Args:
        url: URL string to check
        
    Returns:
        bool: True if URL is absolute (starts with http:// or https://)
    """
    if not url:
        return False
    return url.startswith('http://') or url.startswith('https://')
