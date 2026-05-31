from django.contrib import admin
from .models import Subject, CorrectAnswer, QuestionAnswer, StudentOMR, Result


@admin.register(CorrectAnswer)
class CorrectAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'total_questions')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'correct_answer', 'question_number', 'answer')


@admin.register(StudentOMR)
class StudentOMRAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'roll_number')
    exclude = ('answers',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'result_type', 'marks', 'total_marks')