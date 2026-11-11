from django.contrib import admin
from .models import Student, Feedback


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll', 'phone', 'email', 'gender', 'registered_at')
    search_fields = ('name', 'roll', 'phone', 'email')
    list_filter = ('gender',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'roll_number', 'category', 'rating', 'created_at')
    search_fields = ('student_name', 'roll_number', 'comments')
    list_filter = ('category', 'rating', 'created_at')