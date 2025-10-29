from rest_framework.permissions import BasePermission


class IsDataHost(BasePermission):
    """
    Custom permission to only allow data hosts to access the view.
    Data hosts can create technicians and upload Excel files.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'host'


class IsTechnician(BasePermission):
    """
    Custom permission to only allow technicians to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'technician'


class IsSupervisor(BasePermission):
    """
    Custom permission to only allow supervisors (admins) to access the view.
    Supervisors can monitor and view reports but cannot create/modify data.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'supervisor'


class IsHostOrSupervisor(BasePermission):
    """
    Custom permission to allow both hosts and supervisors to access the view.
    Used for read-only operations like viewing dashboard stats.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['host', 'supervisor']