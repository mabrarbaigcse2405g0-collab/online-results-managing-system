from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("students", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="CorrectAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_questions", models.PositiveIntegerField(default=0)),
                ("answer_key", models.JSONField(blank=True, default=dict)),
                ("answer_file", models.FileField(blank=True, null=True, upload_to="correct_answers/", validators=[django.core.validators.FileExtensionValidator(["json", "txt", "csv", "pdf", "jpg", "jpeg", "png"])])),
                ("subject", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="answer_key", to="omr.subject")),
            ],
        ),
        migrations.CreateModel(
            name="Result",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("result_type", models.CharField(choices=[("OMR", "OMR"), ("CORE", "CORE")], max_length=10)),
                ("marks", models.PositiveIntegerField(default=0)),
                ("total_marks", models.PositiveIntegerField(default=0)),
                ("student_answer_file", models.FileField(blank=True, null=True, upload_to="student_answers/")),
                ("correct_answer_file", models.FileField(blank=True, null=True, upload_to="correct_answers/result_copies/")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="students.student")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="omr.subject")),
            ],
            options={"ordering": ("subject__name", "result_type")},
        ),
        migrations.CreateModel(
            name="StudentOMR",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("roll_number", models.CharField(max_length=20)),
                ("answers", models.JSONField(blank=True, default=dict)),
                ("detected_questions", models.PositiveIntegerField(default=0)),
                ("marks", models.PositiveIntegerField(default=0)),
                ("total_marks", models.PositiveIntegerField(default=0)),
                ("multiple_marked", models.JSONField(blank=True, default=list)),
                ("processing_error", models.TextField(blank=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("omr_file", models.FileField(upload_to="omr/student_papers/", validators=[django.core.validators.FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])])),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="omr_submissions", to="students.student")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="omr_submissions", to="omr.subject")),
            ],
            options={"ordering": ("-uploaded_at",)},
        ),
        migrations.AddConstraint(
            model_name="result",
            constraint=models.UniqueConstraint(fields=("student", "subject", "result_type"), name="unique_student_subject_result_type"),
        ),
    ]
