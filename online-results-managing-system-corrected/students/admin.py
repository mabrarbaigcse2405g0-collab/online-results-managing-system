from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "roll")
    search_fields = ("name", "roll")
    ordering = ("roll",)
# Jenkins test change