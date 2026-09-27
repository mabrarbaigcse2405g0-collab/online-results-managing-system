from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.student_login, name="login"),
    path("logout/", views.student_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
