from django.test import TestCase
from django.urls import reverse

from omr.models import Result, Subject
from students.models import Student

FOOTER_LINES = (
    "MGIT Student Result Management System",
    "Mahatma Gandhi Institute of Technology",
    "&copy; 2026 MGIT",
)


class SiteFooterTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(name="Asha Verma", roll="2405A1")
        subject = Subject.objects.create(name="Python Programming")
        Result.objects.create(
            student=self.student, subject=subject, result_type="CORE",
            marks=28, total_marks=30,
        )
        Result.objects.create(
            student=self.student, subject=subject, result_type="OMR",
            marks=20, total_marks=30,
        )

    def _login(self):
        session = self.client.session
        session["student_id"] = self.student.id
        session.save()

    def assertHasFooter(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<footer class="site-footer">')
        for line in FOOTER_LINES:
            self.assertContains(response, line)

    def test_login_page_has_footer(self):
        self.assertHasFooter(self.client.get(reverse("result_login")))

    def test_login_page_footer_also_shown_on_invalid_login(self):
        response = self.client.post(reverse("result_login"), {"roll": "NOPE"})
        self.assertContains(response, "Invalid roll number")
        self.assertHasFooter(response)

    def test_dashboard_has_footer(self):
        self._login()
        self.assertHasFooter(self.client.get(reverse("dashboard")))

    def test_omr_result_page_has_footer(self):
        self._login()
        self.assertHasFooter(self.client.get(reverse("omr_dashboard")))

    def test_core_result_page_has_footer(self):
        response = self.client.get(reverse("core_result", args=[self.student.id]))
        self.assertHasFooter(response)

    def test_footer_appears_once_per_page(self):
        response = self.client.get(reverse("result_login"))
        self.assertContains(response, '<footer class="site-footer">', count=1)
