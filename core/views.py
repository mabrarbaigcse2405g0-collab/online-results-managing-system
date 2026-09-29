from django.shortcuts import render
from omr.models import Result, Subject
from students.models import Student


def save_core_result(student, subject, core_marks, total_marks):
    """Save or update CORE result for a given student and subject."""
    result, created = Result.objects.get_or_create(
        student=student,
        subject=subject,
        result_type="CORE"
    )

    result.marks = core_marks
    result.total_marks = total_marks
    result.save()
    return result