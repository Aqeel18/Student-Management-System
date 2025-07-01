from django.contrib import admin
from .models import (
    SchoolClass, Division, ClassDivision,
    Subject, DivisionSubject,
    Student, Exam, Mark
)
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

# === SchoolClass Admin with filter_horizontal for subjects ===
class SchoolClassAdmin(admin.ModelAdmin):
    filter_horizontal = ('subjects',)
    list_display = ('name',)

admin.site.register(SchoolClass, SchoolClassAdmin)


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


# === Mark Admin with custom form for bulk marks entry ===
class BulkMarkEntryForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all())
    exam = forms.ModelChoiceField(queryset=Exam.objects.all())

    def __init__(self, *args, **kwargs):
        subjects = kwargs.pop('subjects', None)
        super().__init__(*args, **kwargs)
        if subjects:
            for subject in subjects:
                self.fields[f'subject_{subject.id}'] = forms.FloatField(
                    label=subject.name,
                    required=False,
                    min_value=0,
                    max_value=100,
                )

class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam', 'marks_obtained')
    search_fields = (
        'student__user__username',
        'student__roll_number',
        'subject__name',
        'exam__name',
    )
    list_filter = ('exam', 'subject')
    autocomplete_fields = ('student', 'subject', 'exam')
    change_list_template = 'admin/core/mark/mark_bulk_entry.html'

    def get_relevant_subjects(self, student):
        class_name = student.class_division.student_class.name
        # Try to extract the numeric part of the class name
        try:
            class_num = int(''.join(filter(str.isdigit, class_name)))
        except Exception:
            class_num = None
        if class_num and 1 <= class_num <= 10:
            # 1st to 10th: use SchoolClass.subjects
            return student.class_division.student_class.subjects.all()
        elif class_name.strip().lower() in ['11th', '12th'] or (class_num and class_num in [11, 12]):
            # 11th/12th: use DivisionSubject
            return Subject.objects.filter(
                id__in=DivisionSubject.objects.filter(
                    class_division=student.class_division
                ).values_list('subject_id', flat=True)
            )
        return Subject.objects.none()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-entry/', self.admin_site.admin_view(self.bulk_entry_view), name='core_mark_bulk_entry'),
        ]
        return custom_urls + urls

    def bulk_entry_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
        )
        if request.method == 'POST':
            student_id = request.POST.get('student')
            exam_id = request.POST.get('exam')
            is_step2 = any(k.startswith('subject_') for k in request.POST.keys())
            if student_id and exam_id:
                student = Student.objects.get(pk=student_id)
                exam = Exam.objects.get(pk=exam_id)
                subjects = self.get_relevant_subjects(student)
                if is_step2:
                    form = BulkMarkEntryForm(request.POST, subjects=subjects)
                    if form.is_valid():
                        for subject in subjects:
                            mark_val = form.cleaned_data.get(f'subject_{subject.id}')
                            if mark_val is not None:
                                Mark.objects.update_or_create(
                                    student=student, subject=subject, exam=exam,
                                    defaults={'marks_obtained': mark_val}
                                )
                        messages.success(request, 'Marks saved successfully!')
                        return redirect('..')
                    context['form'] = form
                    context['step'] = 2
                else:
                    form = BulkMarkEntryForm(initial={'student': student, 'exam': exam}, subjects=subjects)
                    context['form'] = form
                    context['step'] = 2
                return render(request, 'admin/core/mark/mark_bulk_entry.html', context)
        form = BulkMarkEntryForm()
        context['form'] = form
        context['step'] = 1
        return render(request, 'admin/core/mark/mark_bulk_entry.html', context)

admin.site.register(Mark, MarkAdmin)


# ✅ Register remaining models (no customization needed)
admin.site.register(Division)
admin.site.register(ClassDivision)
admin.site.register(DivisionSubject)
