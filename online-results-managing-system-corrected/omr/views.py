from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from students.models import Student
from .models import Subject, StudentOMR, Result, CorrectAnswer
from .utils import detect_answers, calculate_score


def _student(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return None
    return Student.objects.filter(pk=student_id).first()


def result_login(request):
    from core.views import result_login as login_view
    return login_view(request)


def dashboard(request):
    from core.views import dashboard as dashboard_view
    return dashboard_view(request)


def omr_dashboard(request):
    student = _student(request)
    if student is None:
        return redirect("result_login")

    results = Result.objects.filter(
        student=student,
        result_type=Result.OMR,
    ).select_related("subject")

    return render(request, "omr_dashboard.html", {
        "student": student,
        "results": results,
    })


def core_result_page(request):
    student = _student(request)
    if student is None:
        return redirect("result_login")

    results = Result.objects.filter(
        student=student,
        result_type=Result.CORE,
    ).select_related("subject")

    return render(request, "core_result.html", {
        "student": student,
        "results": results,
    })


@require_http_methods(["GET", "POST"])
def upload_omr(request):
    student = _student(request)
    if student is None:
        return redirect("result_login")

    subjects = Subject.objects.all()

    if request.method == "POST":
        subject = get_object_or_404(Subject, pk=request.POST.get("subject"))
        uploaded = request.FILES.get("omr_image")

        if not uploaded:
            messages.error(request, "Please select an OMR image or PDF.")
            return render(request, "upload.html", {"student": student, "subjects": subjects})

        answer_key_obj = CorrectAnswer.objects.filter(subject=subject).first()
        if not answer_key_obj or not answer_key_obj.answer_key:
            messages.error(request, f"No answer key is configured for {subject.name}.")
            return render(request, "upload.html", {"student": student, "subjects": subjects})

        # Save first so OpenCV/pdf2image can read the file from disk.
        omr = StudentOMR(
            student=student,
            subject=subject,
            roll_number=student.roll,
            omr_file=uploaded,
        )

        try:
            with transaction.atomic():
                omr.save()
                answers, multiple = detect_answers(omr.omr_file.path)
                marks, total = calculate_score(answers, answer_key_obj.answer_key)

                omr.answers = answers
                omr.detected_questions = len(answers)
                omr.marks = marks
                omr.total_marks = total
                omr.multiple_marked = multiple
                omr.save(update_fields=[
                    "answers", "detected_questions", "marks",
                    "total_marks", "multiple_marked"
                ])

                result, _ = Result.objects.update_or_create(
                    student=student,
                    subject=subject,
                    result_type=Result.OMR,
                    defaults={
                        "marks": marks,
                        "total_marks": total,
                    },
                )

                # Copy uploaded and answer-key files to the result when possible.
                result.student_answer_file = omr.omr_file
                if answer_key_obj.answer_file:
                    result.correct_answer_file = answer_key_obj.answer_file
                result.save()

        except Exception as exc:
            omr.processing_error = str(exc)
            omr.save(update_fields=["processing_error"])
            messages.error(request, f"OMR processing failed: {exc}")
            return render(request, "upload.html", {"student": student, "subjects": subjects})

        messages.success(
            request,
            f"{subject.name}: {marks}/{total} marks ({round((marks/total)*100, 2) if total else 0}%)."
        )
        return redirect("omr_dashboard")

    return render(request, "upload.html", {
        "student": student,
        "subjects": subjects,
    })


@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET", "POST"])
def submit_core(request):
    if request.method == "POST":
        student = get_object_or_404(Student, pk=request.POST.get("student_id"))
        subject = get_object_or_404(Subject, pk=request.POST.get("subject_id"))

        try:
            marks = int(request.POST.get("marks"))
            total = int(request.POST.get("total_marks"))
        except (TypeError, ValueError):
            messages.error(request, "Marks and total marks must be numbers.")
            return redirect("submit_core_page")

        if total <= 0 or marks < 0 or marks > total:
            messages.error(request, "Enter valid marks (0 <= marks <= total).")
            return redirect("submit_core_page")

        answer_key = CorrectAnswer.objects.filter(subject=subject).first()
        result, _ = Result.objects.update_or_create(
            student=student,
            subject=subject,
            result_type=Result.CORE,
            defaults={
                "marks": marks,
                "total_marks": total,
                "correct_answer_file": answer_key.answer_file if answer_key and answer_key.answer_file else None,
            },
        )

        messages.success(request, f"CORE result saved for {student.name}.")
        return redirect("submit_core_page")

    return redirect("submit_core_page")


@user_passes_test(lambda u: u.is_staff)
def submit_core_page(request):
    return render(request, "submit_core.html", {
        "students": Student.objects.all().order_by("roll"),
        "subjects": Subject.objects.all(),
    })
