"""
Custom Middleware for Request Validation and Logging
"""

import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests and responses
    """

    def process_request(self, request):
        """Log incoming requests"""
        if request.path.startswith('/api/'):
            logger.info(
                f"API Request: {request.method} {request.path} "
                f"[User: {request.user if request.user.is_authenticated else 'Anonymous'}]"
            )
        return None

    def process_response(self, request, response):
        """Log outgoing responses"""
        if request.path.startswith('/api/'):
            logger.info(
                f"API Response: {request.method} {request.path} "
                f"[Status: {response.status_code}]"
            )
        return response

    def process_exception(self, request, exception):
        """Log exceptions"""
        logger.exception(
            f"API Exception: {request.method} {request.path} "
            f"[Exception: {exception.__class__.__name__}]"
        )
        return None


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate request data and headers
    """

    def process_request(self, request):
        """Validate incoming requests"""
        # Skip validation for non-API endpoints
        if not request.path.startswith('/api/'):
            return None

        # Validate Content-Type for POST/PUT/PATCH requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.META.get('CONTENT_TYPE', '')
            
            # Allow multipart/form-data for file uploads
            if 'multipart/form-data' in content_type:
                return None
            
            # Require application/json for other requests
            if 'application/json' not in content_type:
                logger.warning(
                    f"Invalid Content-Type: {content_type} "
                    f"for {request.method} {request.path}"
                )
                # Allow it but log warning (don't block)
                # return JsonResponse(
                #     {
                #         'error': 'Invalid Content-Type',
                #         'detail': 'Content-Type must be application/json or multipart/form-data'
                #     },
                #     status=400
                # )

        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses
    """

    def process_response(self, request, response):
        """Add security headers"""
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Add CORS headers for API endpoints (if not already set by django-cors-headers)
        if request.path.startswith('/api/'):
            if 'Access-Control-Allow-Origin' not in response:
                # This will be overridden by django-cors-headers if configured
                response['Access-Control-Allow-Origin'] = '*'
        
        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to catch and handle unhandled exceptions
    """

    def process_exception(self, request, exception):
        """Handle unhandled exceptions"""
        # Log the exception
        logger.exception(
            f"Unhandled Exception: {exception.__class__.__name__} "
            f"in {request.method} {request.path}"
        )

        # Return JSON response for API endpoints
        if request.path.startswith('/api/'):
            return JsonResponse(
                {
                    'error': 'Internal Server Error',
                    'detail': 'An unexpected error occurred. Please try again later.'
                },
                status=500
            )

        # Let Django handle non-API exceptions normally
        return None


class RequestSizeLimitMiddleware(MiddlewareMixin):
    """
    Middleware to limit request body size
    """
    MAX_REQUEST_SIZE = 50 * 1024 * 1024  # 50 MB (for file uploads)

    def process_request(self, request):
        """Check request size"""
        content_length = request.META.get('CONTENT_LENGTH')
        
        if content_length:
            try:
                content_length = int(content_length)
                if content_length > self.MAX_REQUEST_SIZE:
                    logger.warning(
                        f"Request too large: {content_length} bytes "
                        f"for {request.method} {request.path}"
                    )
                    return JsonResponse(
                        {
                            'error': 'Request Too Large',
                            'detail': f'Request body must be less than {self.MAX_REQUEST_SIZE / (1024 * 1024)} MB'
                        },
                        status=413
                    )
            except ValueError:
                pass

        return None
