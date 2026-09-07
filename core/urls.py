from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.student_login, name="login"),
    path("logout/", views.student_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create-exam/", views.create_exam, name="create_exam"),
    path("core-result/", views.core_result_view, name="core_result"),
    path("omr-result/", views.omr_result_view, name="omr_result"),
]