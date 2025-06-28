from django.contrib import admin
from .models import (
    Class, Division, ClassDivision,
    Subject, DivisionSubject,
    Student, Exam, Mark
)

# ✅ Student Admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'class_division', 'id_number')
    search_fields = ('user__username', 'roll_number', 'id_number')
    list_filter = ('class_division',)

# ✅ Exam Admin
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'date')
    search_fields = ('name', 'academic_year')
    list_filter = ('academic_year',)

# ✅ Register remaining models
admin.site.register(Class)
admin.site.register(Division)
admin.site.register(ClassDivision)
admin.site.register(Subject)
admin.site.register(DivisionSubject)
admin.site.register(Mark)
