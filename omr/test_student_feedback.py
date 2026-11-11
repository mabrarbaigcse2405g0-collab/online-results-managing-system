from django.test import TestCase
from django.urls import reverse

from students.models import Student, Feedback


class StudentRegistrationTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse("student_register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Registration")
        self.assertContains(response, 'name="roll"')
        self.assertContains(response, 'name="phone"')

    def test_successful_student_registration(self):
        payload = {
            "name": "Akshith Mucharla",
            "roll": "2405A9",
            "phone": "9876543210",
            "email": "akshith@mgit.ac.in",
            "fdname": "Mucharla",
            "gender": "Male"
        }
        response = self.client.post(reverse("student_register"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registration Successful")

        student = Student.objects.get(roll="2405A9")
        self.assertEqual(student.name, "Akshith Mucharla")
        self.assertEqual(student.phone, "9876543210")
        self.assertEqual(student.email, "akshith@mgit.ac.in")
        self.assertEqual(student.gender, "Male")

    def test_registration_validation_phone_digits(self):
        payload = {
            "name": "Akshith",
            "roll": "2405A9",
            "phone": "12345",  # Invalid phone
            "email": "akshith@mgit.ac.in",
            "fdname": "Father",
            "gender": "Male"
        }
        response = self.client.post(reverse("student_register"), payload)
        self.assertContains(response, "Phone number must be 10 digits")
        self.assertFalse(Student.objects.filter(roll="2405A9").exists())


class StudentFeedbackTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(name="Amogh", roll="2405B2")

    def test_feedback_page_loads(self):
        response = self.client.get(reverse("student_feedback"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Result & Academic Feedback")

    def test_feedback_submission(self):
        payload = {
            "roll": "2405B2",
            "name": "Amogh",
            "category": "Results Evaluation",
            "rating": "5",
            "comments": "The automated result evaluation and OMR marks breakdown are very clear and helpful."
        }
        response = self.client.post(reverse("student_feedback"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your feedback has been recorded successfully")

        feedback = Feedback.objects.filter(roll_number="2405B2").first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.student, self.student)
        self.assertContains(response, "Recent Student Feedback Feed")

    def test_login_and_dashboard_links(self):
        login_res = self.client.get(reverse("result_login"))
        self.assertContains(login_res, reverse("student_register"))
        self.assertContains(login_res, reverse("student_feedback"))

        session = self.client.session
        session["student_id"] = self.student.id
        session.save()

        dash_res = self.client.get(reverse("dashboard"))
        self.assertContains(dash_res, reverse("student_register"))
        self.assertContains(dash_res, reverse("student_feedback"))
