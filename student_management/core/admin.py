from django.contrib import admin
from .models import (
    Class, Division, ClassDivision,
    Subject, DivisionSubject,
    Student, Exam, Mark
)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'class_division', 'id_number')
    search_fields = ('user__username', 'roll_number', 'id_number')
    list_filter = ('class_division',)

# Register other models normally
admin.site.register(Class)
admin.site.register(Division)
admin.site.register(ClassDivision)
admin.site.register(Subject)
admin.site.register(DivisionSubject)
admin.site.register(Exam)
admin.site.register(Mark)

