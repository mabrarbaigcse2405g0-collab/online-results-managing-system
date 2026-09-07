from django.urls import path
from . import views

urlpatterns = [
    path("omr-dashboard/", views.omr_dashboard, name="omr_dashboard"),
    path("core-result/", views.core_result_page, name="core_result"),
    path("upload-omr/", views.upload_omr, name="upload_omr"),
]
