from django.test import TestCase
from .models import Subject, Student, Result


class CoreModelTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Data Structures")
        self.student = Student.objects.create(name="Jane Doe", roll="2405G1")

    def test_subject_str(self):
        self.assertEqual(str(self.subject), "Data Structures")

    def test_student_str(self):
        self.assertEqual(str(self.student), "Jane Doe (2405G1)")

    def test_result_total_marks_auto_calculation(self):
        result = Result.objects.create(
            student=self.student,
            subject=self.subject,
            q1a=3, q1b=2,
            q2a=3, q2b=3,
            q3a=2, q3b=1,
            q4a=3, q4b=2,
            q5a=2, q5b=3,
            q6a=1, q6b=2
        )
        # 3+2 + 3+3 + 2+1 + 3+2 + 2+3 + 1+2 = 27
        self.assertEqual(result.total_marks, 27)
        self.assertIn("Jane Doe", str(result))
        self.assertIn("Data Structures", str(result))