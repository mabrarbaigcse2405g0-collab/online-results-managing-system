from django.db import models
from django.core.validators import FileExtensionValidator
import cv2
import numpy as np
from students.models import Student


# 📚 SUBJECT
class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# 📄 CORRECT ANSWER KEY
class CorrectAnswer(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_questions = models.IntegerField()

    def __str__(self):
        return self.subject.name


# ❓ QUESTION ANSWERS
class QuestionAnswer(models.Model):
    correct_answer = models.ForeignKey(
        CorrectAnswer,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question_number = models.IntegerField()
    answer = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.correct_answer.subject.name} - Q{self.question_number}"


# 🔥 OMR PROCESS FUNCTION (IMPROVED)
def process_omr(file_path):
    answers = {}

    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 130, 255, cv2.THRESH_BINARY_INV)[1]

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bubbles = []

    for c in contours:
        area = cv2.contourArea(c)
        if 500 < area < 3000:
            x, y, w, h = cv2.boundingRect(c)
            if 20 < w < 60 and 20 < h < 60:
                bubbles.append((x, y, w, h))

    # SORT properly (row-wise)
    bubbles = sorted(bubbles, key=lambda b: (b[1] // 40, b[0]))

    options = ['A', 'B', 'C', 'D']
    q = 1

    for i in range(0, len(bubbles), 4):
        row = bubbles[i:i+4]

        if len(row) < 4:
            continue

        filled = []

        for j, (x, y, w, h) in enumerate(row):
            roi = thresh[y:y+h, x:x+w]
            total = cv2.countNonZero(roi)
            filled.append((total, options[j]))

        selected = max(filled, key=lambda x: x[0])[1]

        answers[str(q)] = selected
        q += 1

    return answers


# 📷 STUDENT OMR
class StudentOMR(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_omrs"   # ✅ FIXED (no clash)
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)

    omr_file = models.FileField(
        upload_to='omr/student_papers/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        null=True,
        blank=True
    )

    answers = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 PROCESS OMR IMAGE
        if self.omr_file:
            self.answers = process_omr(self.omr_file.path)
            StudentOMR.objects.filter(pk=self.pk).update(answers=self.answers)

        # 🔥 GET CORRECT ANSWERS
        correct_obj = CorrectAnswer.objects.filter(subject=self.subject).first()

        correct_answers = {}
        if correct_obj:
            for q in correct_obj.questions.all():
                correct_answers[str(q.question_number)] = q.answer

        # 🔥 CALCULATE MARKS
        marks = 0
        for q, ans in self.answers.items():
            if correct_answers.get(q) == ans:
                marks += 1

        # 🔥 SAVE RESULT
        result, _ = Result.objects.get_or_create(
            student=self.student,
            subject=self.subject,
            result_type="OMR"
        )

        result.marks = marks
        result.total_marks = len(correct_answers)
        result.student_answer_pdf = self.omr_file
        result.save()

    def __str__(self):
        return f"{self.student} - {self.subject}"


# 🏆 RESULT
class Result(models.Model):
    RESULT_TYPE_CHOICES = (
        ("OMR", "OMR"),
        ("CORE", "CORE"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results"   # ✅ FIXED (no clash)
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    result_type = models.CharField(
        max_length=10,
        choices=RESULT_TYPE_CHOICES,
        default="OMR"
    )

    marks = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)

    student_answer_pdf = models.FileField(
        upload_to='student_answers/',
        null=True,
        blank=True
    )

    correct_answer_file = models.FileField(
        upload_to='correct_answers/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} ({self.result_type})"