from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from omr.models import Result, Subject
from omr.summary import PASS_PERCENTAGE, build_result_summary
from students.models import Student


class _FakeResult:
    def __init__(self, marks, total_marks):
        self.marks = marks
        self.total_marks = total_marks


class BuildResultSummaryTests(SimpleTestCase):
    def test_empty_results_return_none(self):
        self.assertIsNone(build_result_summary([]))

    def test_example_from_requirements(self):
        marks = [70, 65, 80, 75, 60, 75]  # total 425
        summary = build_result_summary([_FakeResult(m, 100) for m in marks])

        self.assertEqual(summary["total_marks"], 425)
        self.assertEqual(summary["subjects"], 6)
        self.assertAlmostEqual(summary["average"], 70.83, places=2)
        self.assertEqual(summary["status"], "PASS")

    def test_fail_when_below_pass_percentage(self):
        summary = build_result_summary([_FakeResult(30, 100), _FakeResult(35, 100)])
        self.assertEqual(summary["status"], "FAIL")

    def test_pass_boundary_is_inclusive(self):
        summary = build_result_summary([_FakeResult(PASS_PERCENTAGE, 100)])
        self.assertEqual(summary["status"], "PASS")

    def test_no_maximum_marks_gives_na_not_a_false_verdict(self):
        summary = build_result_summary([_FakeResult(0, 0)])
        self.assertEqual(summary["status"], "N/A")


class ResultSummaryPageTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(name="Asha Verma", roll="2405A1")
        self.subjects = [
            Subject.objects.create(name=f"Subject {i}") for i in range(1, 7)
        ]

    def _add(self, student, result_type, marks_list, total=100):
        for subject, marks in zip(self.subjects, marks_list):
            Result.objects.create(
                student=student,
                subject=subject,
                result_type=result_type,
                marks=marks,
                total_marks=total,
            )

    def test_core_result_page_shows_summary_from_real_data(self):
        self._add(self.student, "CORE", [70, 65, 80, 75, 60, 75])

        response = self.client.get(reverse("core_result", args=[self.student.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Result Summary")
        self.assertContains(response, "<strong>Total Marks:</strong> 425")
        self.assertContains(response, "<strong>Subjects:</strong> 6")
        self.assertContains(response, "<strong>Average:</strong> 70.83")
        self.assertContains(response, ">PASS</span>")

    def test_core_result_page_shows_fail_status(self):
        self._add(self.student, "CORE", [20, 30, 25, 35, 10, 30])

        response = self.client.get(reverse("core_result", args=[self.student.id]))

        self.assertContains(response, "<strong>Total Marks:</strong> 150")
        self.assertContains(response, ">FAIL</span>")
        self.assertNotContains(response, ">PASS</span>")

    def test_omr_dashboard_shows_summary_for_logged_in_student(self):
        self._add(self.student, "OMR", [70, 65, 80, 75, 60, 75])
        session = self.client.session
        session["student_id"] = self.student.id
        session.save()

        response = self.client.get(reverse("omr_dashboard"))

        self.assertContains(response, "Result Summary")
        self.assertContains(response, "<strong>Total Marks:</strong> 425")
        self.assertContains(response, "<strong>Average:</strong> 70.83")

    def test_summary_only_counts_that_students_and_that_result_types_rows(self):
        other = Student.objects.create(name="Ravi Kumar", roll="2405B2")
        self._add(self.student, "CORE", [50, 50, 50, 50, 50, 50])   # 300
        self._add(self.student, "OMR", [10, 10, 10, 10, 10, 10])    # must not leak into CORE
        self._add(other, "CORE", [90, 90, 90, 90, 90, 90])          # must not leak in

        response = self.client.get(reverse("core_result", args=[self.student.id]))

        self.assertContains(response, "<strong>Total Marks:</strong> 300")
        self.assertContains(response, "<strong>Subjects:</strong> 6")

    def test_no_summary_section_when_student_has_no_results(self):
        response = self.client.get(reverse("core_result", args=[self.student.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No CORE results found")
        self.assertNotContains(response, "Result Summary")
