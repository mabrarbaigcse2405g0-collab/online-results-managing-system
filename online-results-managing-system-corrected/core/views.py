from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from students.models import Student
from omr.models import Subject, Result


def home(request):
    if request.session.get("student_id"):
        return redirect("dashboard")
    return redirect("result_login")


def student_login(request):
    return result_login(request)


def student_logout(request):
    request.session.flush()
    return redirect("result_login")


@require_http_methods(["GET", "POST"])
def result_login(request):
    if request.method == "POST":
        roll = (request.POST.get("roll") or "").strip()
        name = (request.POST.get("name") or "").strip()

        if not roll:
            return render(request, "result_login.html", {"error": "Please enter your roll number."})

        student = Student.objects.filter(roll__iexact=roll).first()
        if student is None or (name and student.name.strip().lower() != name.lower()):
            return render(request, "result_login.html", {"error": "Invalid student details."})

        request.session["student_id"] = student.id
        request.session["student_roll"] = student.roll
        return redirect("dashboard")

    return render(request, "result_login.html")


def _logged_student(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return None
    return Student.objects.filter(pk=student_id).first()


def dashboard(request):
    student = _logged_student(request)
    if student is None:
        return redirect("result_login")

    omr_count = Result.objects.filter(student=student, result_type="OMR").count()
    core_count = Result.objects.filter(student=student, result_type="CORE").count()

    return render(request, "dashboard.html", {
        "student": student,
        "omr_count": omr_count,
        "core_count": core_count,
    })


def omr_result_view(request):
    return redirect("omr_dashboard")


def core_result_view(request):
    return redirect("core_result")


def create_exam(request):
    return redirect("admin:index")


def save_core_result(student, subject, core_marks, total_marks):
    result, _ = Result.objects.update_or_create(
        student=student,
        subject=subject,
        result_type="CORE",
        defaults={
            "marks": int(core_marks),
            "total_marks": int(total_marks),
        },
    )
    return result
