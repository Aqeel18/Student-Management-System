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


# ✅ Subject Admin (required for autocomplete in MarkAdmin)
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# ✅ Exam Admin (already configured correctly)
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'date')
    search_fields = ('name', 'academic_year')
    list_filter = ('academic_year',)


# ✅ Mark Admin (autocomplete + filters + usability)
@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam', 'marks_obtained')
    search_fields = (
        'student__user__username',
        'student__roll_number',
        'subject__name',
        'exam__name',
    )
    list_filter = ('exam', 'subject')
    autocomplete_fields = ('student', 'subject', 'exam')  # ✅ required related models must have search_fields
    # change_form_template = 'admin/core/mark/change_form.html'  # Use custom Jet form template


# ✅ Register remaining models (no customization needed)
admin.site.register(Class)
admin.site.register(Division)
admin.site.register(ClassDivision)
admin.site.register(DivisionSubject)
