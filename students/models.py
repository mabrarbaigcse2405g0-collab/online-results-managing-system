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

    def __str__(self):
        return f"{self.name} ({self.roll})"