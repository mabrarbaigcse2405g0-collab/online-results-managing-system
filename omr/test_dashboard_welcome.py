from django.test import TestCase
from django.urls import reverse

from students.models import Student


class DashboardWelcomeCardTests(TestCase):
    def _login(self, student):
        session = self.client.session
        session["student_id"] = student.id
        session.save()

    def test_welcome_card_shows_logged_in_student_details(self):
        student = Student.objects.create(name="Asha Verma", roll="2405A1")
        self._login(student)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="welcome-card"')
        self.assertContains(response, "Welcome to MGIT Student Result Management System")
        self.assertContains(response, "Asha Verma")
        self.assertContains(response, "2405A1")
        self.assertContains(
            response, "View your academic results and subject-wise marks here."
        )

    def test_welcome_card_uses_each_students_own_data(self):
        Student.objects.create(name="Asha Verma", roll="2405A1")
        other = Student.objects.create(name="Ravi Kumar", roll="2405B2")
        self._login(other)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Ravi Kumar")
        self.assertContains(response, "2405B2")
        self.assertNotContains(response, "Asha Verma")
        self.assertNotContains(response, "2405A1")

    def test_full_login_flow_lands_on_dashboard_with_card(self):
        Student.objects.create(name="Asha Verma", roll="2405A1")

        response = self.client.post(
            reverse("result_login"), {"roll": "2405A1"}, follow=True
        )

        self.assertEqual(response.redirect_chain[-1][0], reverse("dashboard"))
        self.assertContains(response, 'class="welcome-card"')
        self.assertContains(response, "Asha Verma")

    def test_dashboard_still_redirects_when_not_logged_in(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("result_login"))
