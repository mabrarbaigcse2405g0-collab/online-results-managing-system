from django.db import models
from django.core.validators import FileExtensionValidator
from students.models import Student


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class CorrectAnswer(models.Model):
    subject = models.OneToOneField(
        Subject,
        on_delete=models.CASCADE,
        related_name="answer_key",
    )
    total_questions = models.PositiveIntegerField(default=0)
    answer_key = models.JSONField(default=dict, blank=True)
    answer_file = models.FileField(
        upload_to="correct_answers/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["json", "txt", "csv", "pdf", "jpg", "jpeg", "png"])],
    )

    def save(self, *args, **kwargs):
        if self.answer_key:
            self.answer_key = {
                str(k): str(v).strip().upper()
                for k, v in self.answer_key.items()
                if str(k).strip()
            }
            self.total_questions = max(
                self.total_questions or 0,
                len(self.answer_key),
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer Key - {self.subject.name}"


class StudentOMR(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="omr_submissions",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="omr_submissions",
    )
    roll_number = models.CharField(max_length=20)
    omr_file = models.FileField(
        upload_to="omr/student_papers/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
    )
    answers = models.JSONField(default=dict, blank=True)
    detected_questions = models.PositiveIntegerField(default=0)
    marks = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    multiple_marked = models.JSONField(default=list, blank=True)
    processing_error = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at",)

    def __str__(self):
        return f"{self.student.roll} - {self.subject.name}"


class Result(models.Model):
    OMR = "OMR"
    CORE = "CORE"
    RESULT_TYPE_CHOICES = (
        (OMR, "OMR"),
        (CORE, "CORE"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="results",
    )
    result_type = models.CharField(
        max_length=10,
        choices=RESULT_TYPE_CHOICES,
    )
    marks = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    student_answer_file = models.FileField(
        upload_to="student_answers/",
        null=True,
        blank=True,
    )
    correct_answer_file = models.FileField(
        upload_to="correct_answers/result_copies/",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("student", "subject", "result_type"),
                name="unique_student_subject_result_type",
            )
        ]
        ordering = ("subject__name", "result_type")

    @property
    def percentage(self):
        if not self.total_marks:
            return 0
        return round((self.marks / self.total_marks) * 100, 2)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.result_type}"
