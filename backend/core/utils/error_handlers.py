"""
Custom Exception Handlers for Django REST Framework
Provides consistent error responses across the API
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotFound,
    AuthenticationFailed
)
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Get the view and request from context
    view = context.get('view', None)
    request = context.get('request', None)

    # Log the error
    if request:
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)} "
            f"[{request.method} {request.path}]"
        )

    # Handle Django's ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            return Response(
                {
                    'error': 'Validation Error',
                    'details': exc.message_dict
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif hasattr(exc, 'messages'):
            return Response(
                {
                    'error': 'Validation Error',
                    'detail': exc.messages[0] if exc.messages else 'Invalid data'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # Handle DRF's ValidationError
    if isinstance(exc, ValidationError):
        return Response(
            {
                'error': 'Validation Error',
                'details': exc.detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle PermissionDenied
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                'error': 'Permission Denied',
                'detail': str(exc) or 'You do not have permission to perform this action.'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Handle NotFound / Http404
    if isinstance(exc, (NotFound, Http404)):
        return Response(
            {
                'error': 'Not Found',
                'detail': str(exc) or 'The requested resource was not found.'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Handle AuthenticationFailed
    if isinstance(exc, AuthenticationFailed):
        return Response(
            {
                'error': 'Authentication Failed',
                'detail': str(exc) or 'Invalid or expired authentication credentials.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # If response is None, it's an unhandled exception
    if response is None:
        logger.exception(f"Unhandled exception: {exc}")
        return Response(
            {
                'error': 'Internal Server Error',
                'detail': 'An unexpected error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Customize the response format for other exceptions
    if response is not None:
        # Ensure consistent error response format
        if isinstance(response.data, dict):
            if 'detail' not in response.data and 'error' not in response.data:
                response.data = {
                    'error': exc.__class__.__name__,
                    'detail': str(exc)
                }
        else:
            response.data = {
                'error': exc.__class__.__name__,
                'detail': str(response.data)
            }

    return response


class APIException(Exception):
    """Base class for custom API exceptions"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail

        if status_code is not None:
            self.status_code = status_code


class BadRequestException(APIException):
    """400 Bad Request"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request.'


class UnauthorizedException(APIException):
    """401 Unauthorized"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided or are invalid.'


class ForbiddenException(APIException):
    """403 Forbidden"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'


class NotFoundException(APIException):
    """404 Not Found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'


class ConflictException(APIException):
    """409 Conflict"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict.'


class ValidationException(APIException):
    """422 Unprocessable Entity"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Validation error.'


def handle_api_exception(exc):
    """
    Helper function to handle custom API exceptions
    """
    logger.error(f"API Exception: {exc.__class__.__name__} - {exc.detail}")
    return Response(
        {
            'error': exc.__class__.__name__,
            'detail': exc.detail
        },
        status=exc.status_code
    )
