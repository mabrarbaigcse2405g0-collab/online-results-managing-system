from django.urls import path
from . import views
from django.test import TestCase

urlpatterns = [
    path('create-exam/', views.create_exam, name='create_exam'),
    path('login/', views.student_login, name='login'),
    path('', views.home, name='home'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
]
#hello world