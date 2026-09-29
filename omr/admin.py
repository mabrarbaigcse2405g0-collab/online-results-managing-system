from django.contrib import admin
from .models import Subject, CorrectAnswer, QuestionAnswer, StudentOMR, Result


@admin.register(CorrectAnswer)
class CorrectAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'total_questions')
    list_filter = ('subject',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'correct_answer', 'question_number', 'answer')
    list_filter = ('correct_answer__subject',)
    ordering = ('correct_answer', 'question_number')


@admin.register(StudentOMR)
class StudentOMRAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'roll_number')
    search_fields = ('student__name', 'roll_number')
    list_filter = ('subject',)
    exclude = ('answers',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'result_type', 'marks', 'total_marks')
    list_filter = ('result_type', 'subject')
    search_fields = ('student__name', 'student__roll')