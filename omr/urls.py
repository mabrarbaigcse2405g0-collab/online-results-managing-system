from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    # NEW
    path('omr-dashboard/', views.omr_dashboard, name='omr_dashboard'),
    path('core-result/<int:student_id>/', views.core_result_page, name='core_result'),
]