from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from . import views_admin

app_name = 'core'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Data Host endpoints
    path('host/technicians/', views.technicians_view, name='technicians'),
    path('host/upload-excel', views.upload_excel, name='upload_excel'),
    path('host/dashboard-stats', views.dashboard_stats, name='dashboard_stats'),
    
    # Technician endpoints
    path('technician/my-excel-data', views.get_my_excel_data, name='my_excel_data'),
    path('technician/devices', views.technician_devices_view, name='technician_devices'),
    path('technician/submit', views.submit_maintenance, name='submit_maintenance'),
    
    # Supervisor endpoints
    path('supervisor/submissions', views_admin.get_submissions, name='get_submissions'),
    path('supervisor/submissions/<int:submission_id>', views_admin.get_submission_detail, name='get_submission_detail'),
    path('supervisor/submissions/<int:submission_id>/approve', views_admin.approve_submission, name='approve_submission'),
    path('supervisor/submissions/<int:submission_id>/reject', views_admin.reject_submission, name='reject_submission'),
    path('supervisor/submissions/<int:submission_id>/preview-pdf', views_admin.preview_pdf, name='preview_pdf'),
    path('supervisor/dashboard-stats', views_admin.get_dashboard_stats, name='supervisor_dashboard_stats'),
]