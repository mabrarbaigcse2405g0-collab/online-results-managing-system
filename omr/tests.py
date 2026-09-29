from django.test import TestCase, Client
from django.urls import reverse
from students.models import Student
from omr.models import Subject, Result


class OMRAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(name="Test Student", roll="2405G0")
        self.subject = Subject.objects.create(name="Python Programming")

    def test_subject_str(self):
        self.assertEqual(str(self.subject), "Python Programming")

    def test_result_login_page_renders(self):
        response = self.client.get(reverse("result_login"))
        self.assertEqual(response.status_code, 200)

    def test_result_login_success(self):
        response = self.client.post(reverse("result_login"), {"roll": "2405G0"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("student_id"), self.student.id)

    def test_result_login_invalid_roll(self):
        response = self.client.post(reverse("result_login"), {"roll": "INVALID_ROLL"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid roll number")

    def test_student_logout(self):
        # Set session
        session = self.client.session
        session["student_id"] = self.student.id
        session.save()

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("student_id", self.client.session)

    def test_core_result_page(self):
        Result.objects.create(
            student=self.student,
            subject=self.subject,
            result_type="CORE",
            marks=28,
            total_marks=30
        )
        response = self.client.get(reverse("core_result", args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")