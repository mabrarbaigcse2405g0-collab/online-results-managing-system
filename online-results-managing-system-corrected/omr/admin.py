from django import forms
from django.contrib import admin

from .models import Subject, CorrectAnswer, StudentOMR, Result


class CorrectAnswerAdminForm(forms.ModelForm):
    total_questions = forms.IntegerField(
        min_value=1,
        max_value=200,
        label="Total questions",
        widget=forms.NumberInput(attrs={
            "min": 1,
            "max": 200,
            "id": "id_total_questions",
        }),
    )

    answer_key = forms.JSONField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "id_answer_key"}),
    )

    class Meta:
        model = CorrectAnswer
        fields = ("subject", "total_questions", "answer_key", "answer_file")

    def clean(self):
        cleaned = super().clean()
        total = cleaned.get("total_questions")
        answer_key = cleaned.get("answer_key") or {}

        if total and len(answer_key) != total:
            raise forms.ValidationError(
                f"Please select one correct option for all {total} questions."
            )

        expected = {str(i) for i in range(1, total + 1)} if total else set()
        if set(str(k) for k in answer_key.keys()) != expected:
            raise forms.ValidationError(
                "Answer key must contain exactly one answer for every question."
            )

        for question, answer in answer_key.items():
            if str(answer) not in {"1", "2", "3", "4"}:
                raise forms.ValidationError(
                    f"Question {question} must have a correct option from 1, 2, 3, or 4."
                )

        cleaned["answer_key"] = {str(k): str(v) for k, v in answer_key.items()}
        return cleaned


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(CorrectAnswer)
class CorrectAnswerAdmin(admin.ModelAdmin):
    form = CorrectAnswerAdminForm
    list_display = ("subject", "total_questions")
    search_fields = ("subject__name",)

    class Media:
        js = ("omr/js/correct_answer_admin.js",)


@admin.register(StudentOMR)
class StudentOMRAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student", "subject", "marks",
        "total_marks", "detected_questions", "uploaded_at"
    )
    list_filter = ("subject", "uploaded_at")
    search_fields = ("student__name", "student__roll")
    readonly_fields = (
        "answers", "detected_questions", "marks",
        "total_marks", "multiple_marked", "processing_error",
        "uploaded_at",
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "result_type", "marks", "total_marks", "updated_at")
    list_filter = ("result_type", "subject")
    search_fields = ("student__name", "student__roll", "subject__name")
