from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Subject, StudentOMR, Result, CorrectAnswer
from students.models import Student
from .summary import build_result_summary

import cv2
import numpy as np


# =========================
# MOCK OMR LOGIC
# =========================
def process_omr(img):
    return {
        "q1": 1,
        "q2": 2,
        "q3": 1,
        "q4": 3,
        "q5": 2
    }


# =========================
# MAIN DASHBOARD
# =========================
def dashboard(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("result_login")

    student = get_object_or_404(Student, id=student_id)

    return render(request, "dashboard.html", {
        "student": student
    })


# =========================
# OMR DASHBOARD
# =========================
def omr_dashboard(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("result_login")

    student = get_object_or_404(Student, id=student_id)

    # ✅ ONLY OMR
    results = Result.objects.filter(
        student=student,
        result_type="OMR"
    )

    for r in results:
        r.percentage = (r.marks / r.total_marks) * 100 if r.total_marks else 0

    return render(request, "omr_dashboard.html", {
        "student": student,
        "results": results,
        "summary": build_result_summary(results)
    })


# =========================
# CORE RESULT PAGE
# =========================

def core_result_page(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    results = Result.objects.filter(
        student=student,
        result_type="CORE"
    )

    for r in results:
        r.percentage = (r.marks / r.total_marks) * 100 if r.total_marks else 0

    return render(request, "core_result.html", {
        "student": student,
        "results": results,
        "summary": build_result_summary(results)
    })


# =========================
# LOGIN & LOGOUT
# =========================
def result_login(request):
    if request.method == "POST":
        roll = request.POST.get("roll", "").strip()

        try:
            student = Student.objects.get(roll__iexact=roll)
            request.session["student_id"] = student.id
            return redirect("dashboard")

        except Student.DoesNotExist:
            return render(request, "result_login.html", {
                "error": "Invalid roll number"
            })

    return render(request, "result_login.html")


def student_logout(request):
    request.session.flush()
    return redirect("result_login")


# =========================
# UPLOAD OMR (FIXED FULL)
# =========================
@csrf_exempt
def upload_omr(request):
    if request.method == "POST":

        file = request.FILES.get("omr_image")
        roll = request.POST.get("roll")
        subject_id = request.POST.get("subject")

        student = get_object_or_404(Student, roll=roll)
        subject = get_object_or_404(Subject, id=subject_id)

        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        answers = process_omr(img)

        omr = StudentOMR.objects.create(
            student=student,
            subject=subject,
            roll_number=roll,
            omr_file=file,
            answers=answers
        )

        result, created = Result.objects.get_or_create(
            student=student,
            subject=subject,
            result_type="OMR"
        )

        result.marks = sum(answers.values())
        result.total_marks = 30

        if file:
            file.seek(0)
            result.student_answer_pdf.save(file.name, file, save=False)

        result.save()

        return redirect("omr_dashboard")


# =========================
# SUBMIT CORE RESULT
# =========================
def submit_core(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        subject_id = request.POST.get("subject_id")
        marks = request.POST.get("marks", 0)
        total_marks = request.POST.get("total_marks", 0)

        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # ✅ CREATE CORE RESULT
        result, created = Result.objects.get_or_create(
            student=student,
            subject=subject,
            result_type="CORE"
        )

        # ✅ SAVE MARKS
        result.marks = marks
        result.total_marks = total_marks

        # 🔥 GET ADMIN UPLOADED FILES (SAFE LOOKUP)
        correct_obj = CorrectAnswer.objects.filter(subject=subject).first()

        if correct_obj:
            if hasattr(correct_obj, 'student_answer_file'):
                result.student_answer_pdf = correct_obj.student_answer_file
            if hasattr(correct_obj, 'correct_answer_file'):
                result.correct_answer_file = correct_obj.correct_answer_file

        # ✅ SAVE FINAL
        result.save()

        return redirect("core_result", student_id=student.id)

    return redirect("submit_core_page")


def submit_core_page(request):
    return render(request, "submit_core.html")


def student_profile(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("result_login")
    student = get_object_or_404(Student, id=student_id)
    return render(request, "dashboard.html", {"student": student})
   