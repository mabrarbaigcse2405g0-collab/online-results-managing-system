# Online Results Management System

Django project with:
- Student login
- OMR upload and bubble detection
- Answer-key based automatic marking
- CORE/manual result entry
- Student dashboard
- Django admin management

## First run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- Student portal: http://127.0.0.1:8000/result-login/
- Admin: http://127.0.0.1:8000/admin/

## Configure data

1. Log in to Django admin.
2. Create Students.
3. Create Subjects.
4. Create one Correct Answer entry per subject.
5. Put the answer key in JSON format, for example:
   `{"1":"A","2":"C","3":"B","4":"D"}`
6. Optionally upload the correct-answer file.
7. Use **CORE Result Entry** after logging in as a staff user, or use the Django admin to create CORE results.
8. Student logs in and uploads their OMR sheet.

## OMR format

The detector is designed for a clear, straight answer sheet with four bubbles per question in A/B/C/D order. It uses contour filtering and fill-ratio comparison. If your actual OMR sheet has a different layout, the detector must be calibrated to that sheet.
