"""Result summary calculation for the student result pages.

All values are computed from the student's existing Result rows
(marks / total_marks); nothing here is hardcoded per student.
"""

# Overall percentage (total marks obtained / total marks available) needed to PASS.
# Change this single value if the college uses a different pass mark.
PASS_PERCENTAGE = 40


def build_result_summary(results):
    """Return a summary dict for an iterable of Result objects, or None if empty.

    Keys: total_marks, subjects, average, percentage, status ("PASS"/"FAIL"/"N/A").
    """
    results = list(results)
    subjects = len(results)
    if subjects == 0:
        return None

    total_marks = sum(r.marks for r in results)
    max_marks = sum(r.total_marks for r in results)
    average = total_marks / subjects

    if max_marks > 0:
        percentage = total_marks / max_marks * 100
        status = "PASS" if percentage >= PASS_PERCENTAGE else "FAIL"
    else:
        # No maximum marks recorded, so a pass/fail decision cannot be made.
        percentage = 0
        status = "N/A"

    return {
        "total_marks": total_marks,
        "subjects": subjects,
        "average": average,
        "percentage": percentage,
        "status": status,
    }
