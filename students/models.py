from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll = models.CharField(max_length=20, unique=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="students",  # ✅ IMPORTANT FIX
        null=True,
        blank=True
    )

    result = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ])
    registered_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.roll})"


class Feedback(models.Model):
    CATEGORY_CHOICES = (
        ("Results Evaluation", "Results Evaluation"),
        ("Course Content", "Course Content"),
        ("OMR Scanning", "OMR Scanning"),
        ("General Feedback", "General Feedback"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        null=True,
        blank=True
    )
    roll_number = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default="Results Evaluation", choices=CATEGORY_CHOICES)
    rating = models.IntegerField(default=5)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} ({self.roll_number}) - Rating: {self.rating}/5"