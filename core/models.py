from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Jenkins test change
# ✅ SUBJECT
class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ✅ STUDENT
class Student(models.Model):
    name = models.CharField(max_length=100)
    roll = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.roll})"


# ✅ CORRECT ANSWERS (QUESTION-WISE)
class CorrectAnswer(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    # 🔥 THIS IS WHAT YOU WANT
    answer_file = models.FileField(
    upload_to='core/correct_answers/',
    null=True,
    blank=True
)
    def __str__(self):
        return f"Correct - {self.subject.name}"


# ✅ STUDENT ANSWER (ADD FILE FIELD)
class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    # 🔥 THIS IS WHAT YOU WANT
    answer_file = models.FileField(
    upload_to='core/student_answers/',
    null=True,
    blank=True
)
    def __str__(self):
        return f"{self.student.name} - {self.subject.name}"


# ✅ RESULT
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    # ✅ Question-wise marks (each max = 3)
    q1a = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    q1b = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    q2a = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    q2b = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    q3a = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    q3b = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    q4a = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    q4b = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    q5a = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    q5b = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    q6a = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    q6b = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    # ✅ Auto total
    total_marks = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_marks = (
            self.q1a + self.q1b +
            self.q2a + self.q2b +
            self.q3a + self.q3b +
            self.q4a + self.q4b +
            self.q5a + self.q5b +
            self.q6a + self.q6b
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.total_marks}"