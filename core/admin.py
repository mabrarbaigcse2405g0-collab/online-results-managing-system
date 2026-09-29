# This is Sai Krishna

from django.contrib import admin
from .models import Subject, Student, CorrectAnswer, StudentAnswer, Result


@admin.register(Subject)
class CoreSubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Student)
class CoreStudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'roll')
    search_fields = ('name', 'roll')


@admin.register(CorrectAnswer)
class CoreCorrectAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'answer_file')
    list_filter = ('subject',)


@admin.register(StudentAnswer)
class CoreStudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'answer_file')
    list_filter = ('subject',)
    search_fields = ('student__name', 'student__roll')


@admin.register(Result)
class CoreResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'total_marks')
    list_filter = ('subject',)
    search_fields = ('student__name', 'student__roll')