"""
This is Gowtham Varma
"""

from django.contrib import admin
from django.urls import path
from omr import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.result_login, name='home'),
    path('admin/', admin.site.urls),

    path('result-login/', views.result_login, name='result_login'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('omr-dashboard/', views.omr_dashboard, name='omr_dashboard'),

    path('core-result/<int:student_id>/', views.core_result_page, name='core_result'),

    path('submit-core/', views.submit_core, name='submit_core'),

    path('submit-core-page/', views.submit_core_page, name='submit_core_page'),

    # New feature
    path('student-profile/', views.student_profile, name='student_profile'),
    path('logout/', views.student_logout, name='logout'),
]


# ✅ ONLY ONCE (IMPORTANT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)