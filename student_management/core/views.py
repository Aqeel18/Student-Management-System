from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Student, Mark, Exam, Subject, Division, ClassSection, Teacher, Class
from .forms import ExamForm, StudentForm, SubjectForm, DivisionForm, MarkForm, ClassSectionForm, TeacherForm, ClassForm, UserForm, StudentProfileForm, StudentMarksEntryForm
from django.contrib.auth import logout
from .decorators import student_required, admin_required
from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views import View
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.db.models import Count, Avg
from django.db import transaction

def custom_logout_view(request):
    logout(request)
    return redirect('/admin/login/')



@student_required
@login_required
def home_view(request):
    # Always show student dashboard or login page
    if not request.user.is_authenticated:
        return redirect('/login/')
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return redirect('/login/')

    # ✅ Fetch marks grouped by exam
    marks = Mark.objects.filter(student=student).select_related('exam', 'subject')

    exam_results = {}
    for mark in marks:
        exam = mark.exam
        if exam not in exam_results:
            exam_results[exam] = []
        exam_results[exam].append(mark)

    # --- Results Summary logic ---
    latest_exam = Exam.objects.order_by('-date').first()
    results_summary = None
    if latest_exam:
        latest_marks = Mark.objects.filter(student=student, exam=latest_exam)
        if latest_marks.exists():
            avg_score = sum(m.marks_obtained for m in latest_marks) / latest_marks.count()
            results_summary = {
                'exam_name': latest_exam.name,
                'exam_date': latest_exam.date,
                'average_score': round(avg_score, 2),
            }

    # To get all subjects for the student's class:
    subjects = student.class_division.student_class.subjects.all()
    # (student_class is now a SchoolClass instance)

    return render(request, 'core/student_dashboard.html', {
        'student': student,
        'exam_results': exam_results,
        'results_summary': results_summary,
    })


@student_required
@login_required
def student_profile_view(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return HttpResponse("Student profile not found. Please contact the administrator.")

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student-profile')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'core/student_profile.html', {
        'form': form,
        'student': student,
    })


@student_required
@login_required
def student_results(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return HttpResponse("Student profile not found. Please contact the administrator.")

    marks = Mark.objects.filter(student=student).select_related('exam', 'subject')
    exam_results = {}
    for mark in marks:
        exam = mark.exam
        if exam not in exam_results:
            exam_results[exam] = []
        exam_results[exam].append(mark)

    return render(request, 'core/student_results.html', {
        'exam_results': exam_results,
    })


class StudentLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class StudentLoginView(View):
    template_name = 'registration/login.html'
    form_class = StudentLoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    messages.error(request, "Staff/admin users must log in via the admin panel.")
                    return render(request, self.template_name, {'form': form})
                auth_login(request, user)
                return redirect(reverse('home'))
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {'form': form})


class AdminLoginView(auth_views.LoginView):
    template_name = 'registration/admin_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('dashboard')


def index(request):
    return admin_required(lambda request: render(request, 'core/dashboard.html'))(request)

def base(request):
    return admin_required(lambda request: render(request, 'core/dashboardbase.html'))(request)

def manage_students_view(request):
    return admin_required(lambda request: render(request, 'core/manage_students.html'))(request)

def manage_exams_view(request):
    return admin_required(lambda request: render(request, 'core/manage_exams.html'))(request)

def manage_subjects_view(request):
    return admin_required(lambda request: render(request, 'core/manage_subjects.html'))(request)

def manage_classes_view(request):
    return admin_required(lambda request: render(request, 'core/manage_classes.html'))(request)

def marks_entry_view(request):
    return admin_required(lambda request: render(request, 'core/marks_entry.html'))(request)

def bulk_upload_view(request):
    return admin_required(lambda request: render(request, 'core/bulk_upload.html'))(request)

def id_card_generator_view(request):
    return admin_required(lambda request: render(request, 'core/id_card_generator.html'))(request)

def reports_view(request):
    return admin_required(lambda request: render(request, 'core/reports.html'))(request)


# --- Dashboard ---
@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def dashboard(request):
    context = {
        'total_students': Student.objects.count(),
        'total_exams': Exam.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_classdivs': ClassSection.objects.count(),
        'recent_students': Student.objects.order_by('-id')[:5],
        'recent_exams': Exam.objects.order_by('-date')[:5],
        'recent_marks': Mark.objects.order_by('-id')[:5],
        'upcoming_exams': Exam.objects.order_by('date')[:5],
        'class_labels': list(ClassSection.objects.values_list('school_class__name', flat=True).distinct()),
        'class_counts': list(ClassSection.objects.values('school_class__name').annotate(count=Count('student')).values_list('count', flat=True)),
        'avg_scores': list(Mark.objects.values('student__class_section__school_class__name').annotate(avg=Avg('marks_obtained')).values_list('avg', flat=True)),
    }
    return render(request, 'core/dashboardbase.html', context)

# --- List all ClassSections ---
def class_section_list(request):
    sections = ClassSection.objects.select_related('school_class', 'division', 'teacher').all()
    return render(request, 'core/section_list.html', {'sections': sections})

@login_required
@user_passes_test(lambda u: u.is_staff)
def class_section_create(request):
    if request.method == 'POST':
        form = ClassSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class section added successfully.')
            return redirect('class_section_list')
    else:
        form = ClassSectionForm()
    return render(request, 'core/class_section_edit.html', {'form': form, 'is_create': True})

@login_required
@user_passes_test(lambda u: u.is_staff)
def class_section_edit(request, pk):
    section = get_object_or_404(ClassSection, pk=pk)
    if request.method == 'POST':
        form = ClassSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class section updated successfully.')
            return redirect('class_section_list')
    else:
        form = ClassSectionForm(instance=section)
    return render(request, 'core/class_section_edit.html', {'form': form, 'section': section, 'is_create': False})

@login_required
@user_passes_test(lambda u: u.is_staff)
def class_section_delete(request, pk):
    section = get_object_or_404(ClassSection, pk=pk)
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Class section deleted successfully.')
        return redirect('class_section_list')
    return render(request, 'core/class_section_delete.html', {'section': section})

@login_required
@user_passes_test(lambda u: u.is_staff)
def class_section_detail(request, pk):
    section = get_object_or_404(ClassSection, pk=pk)
    students = Student.objects.filter(class_section=section)
    return render(request, 'core/section_detail.html', {'section': section, 'students': students})

@login_required
@user_passes_test(lambda u: u.is_staff)
def section_marks_entry(request, section_id):
    section = get_object_or_404(ClassSection, pk=section_id)
    students = Student.objects.filter(class_section=section)
    subjects = section.subjects.all()
    exams = Exam.objects.all()
    selected_exam_id = request.POST.get('exam') or request.GET.get('exam')
    selected_exam = None
    if selected_exam_id:
        selected_exam = get_object_or_404(Exam, pk=selected_exam_id)
    MarkFormSet = forms.modelformset_factory(Mark, form=MarkForm, extra=0, can_delete=False)
    initial_data = []
    if selected_exam:
        for student in students:
            for subject in subjects:
                initial_data.append({'student': student, 'subject': subject, 'exam': selected_exam})
    if request.method == 'POST' and selected_exam:
        formset = MarkFormSet(request.POST, queryset=Mark.objects.none(), initial=initial_data)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Marks saved successfully.')
            return redirect('class_section_detail', pk=section.pk)
    else:
        formset = MarkFormSet(queryset=Mark.objects.none(), initial=initial_data)
    return render(request, 'core/section_marks_entry.html', {
        'section': section,
        'students': students,
        'exams': exams,
        'selected_exam': selected_exam,
    })

def student_list(request):
    students = Student.objects.select_related('class_section').all()
    return render(request, 'core/student_list.html', {'students': students})

@login_required
@user_passes_test(lambda u: u.is_staff)
def student_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.save()
                student = student_form.save(commit=False)
                student.user = user
                student.save()
            messages.success(request, 'Student and user account created successfully!')
            return redirect('student_list')
    else:
        user_form = UserForm()
        student_form = StudentForm()
    return render(request, 'core/student_form.html', {'user_form': user_form, 'student_form': student_form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        student_form = StudentForm(request.POST, instance=student)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data.get('password'):
                user.set_password(user_form.cleaned_data['password'])
            user.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            messages.success(request, 'Student and user updated successfully.')
            return redirect('student_list')
    else:
        user_form = UserForm(instance=user)
        student_form = StudentForm(instance=student)
    return render(request, 'core/student_edit.html', {
        'user_form': user_form,
        'student_form': student_form,
        'student': student,
        'is_create': False
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('student_list')
    return render(request, 'core/student_delete.html', {'student': student})

def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'core/teacher_list.html', {'teachers': teachers})

@login_required
@user_passes_test(lambda u: u.is_staff)
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher added successfully.')
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'core/teacher_edit.html', {'form': form, 'is_create': True})

@login_required
@user_passes_test(lambda u: u.is_staff)
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully.')
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'core/teacher_edit.html', {'form': form, 'teacher': teacher, 'is_create': False})

@login_required
@user_passes_test(lambda u: u.is_staff)
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
        return redirect('teacher_list')
    return render(request, 'core/teacher_delete.html', {'teacher': teacher})

def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'core/subject_list.html', {'subjects': subjects})

@login_required
@user_passes_test(lambda u: u.is_staff)
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'core/subject_edit.html', {'form': form, 'is_create': True})

@login_required
@user_passes_test(lambda u: u.is_staff)
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'core/subject_edit.html', {'form': form, 'subject': subject, 'is_create': False})

@login_required
@user_passes_test(lambda u: u.is_staff)
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('subject_list')
    return render(request, 'core/subject_delete.html', {'subject': subject})

def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'core/exam_list.html', {'exams': exams})

@login_required
@user_passes_test(lambda u: u.is_staff)
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam added successfully.')
            return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'core/exam_edit.html', {'form': form, 'is_create': True})

@login_required
@user_passes_test(lambda u: u.is_staff)
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated successfully.')
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'core/exam_edit.html', {'form': form, 'exam': exam, 'is_create': False})

@login_required
@user_passes_test(lambda u: u.is_staff)
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted successfully.')
        return redirect('exam_list')
    return render(request, 'core/exam_delete.html', {'exam': exam})

def mark_report(request):
    marks = Mark.objects.select_related('student', 'exam', 'subject')
    exams = Exam.objects.all()
    subjects = Subject.objects.all()
    student_query = request.GET.get('student', '')
    exam_id = request.GET.get('exam', '')
    subject_id = request.GET.get('subject', '')
    if student_query:
        marks = marks.filter(student__name__icontains=student_query)
    if exam_id:
        marks = marks.filter(exam_id=exam_id)
    if subject_id:
        marks = marks.filter(subject_id=subject_id)
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mark_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Exam', 'Subject', 'Marks'])
        for mark in marks:
            writer.writerow([mark.student.name, mark.exam.name, mark.subject.name, mark.marks_obtained])
        return response
    return render(request, 'core/mark_report.html', {'marks': marks, 'exams': exams, 'subjects': subjects})

@login_required
@user_passes_test(lambda u: u.is_staff)
def excel_upload(request):
    import io
    import pandas as pd
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file)
        for _, row in df.iterrows():
            student, _ = Student.objects.get_or_create(name=row['Student'])
            exam, _ = Exam.objects.get_or_create(name=row['Exam'])
            subject, _ = Subject.objects.get_or_create(name=row['Subject'])
            Mark.objects.update_or_create(
                student=student, exam=exam, subject=subject,
                defaults={'marks_obtained': row['Marks']}
            )
        messages.success(request, 'Excel uploaded and marks imported.')
    return render(request, 'core/excel_upload.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def id_cards(request):
    sections = ClassSection.objects.all()
    students = []
    section_id = request.GET.get('class_section')
    if section_id:
        students = Student.objects.filter(class_section_id=section_id)
    return render(request, 'core/id_cards.html', {'sections': sections, 'students': students})

@login_required
@user_passes_test(lambda u: u.is_staff)
def settings(request):
    school_name = 'My School'
    if request.method == 'POST':
        school_name = request.POST.get('school_name', school_name)
        messages.success(request, 'Settings saved.')
    return render(request, 'core/settings.html', {'school_name': school_name})

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_classes(request):
    classes = Class.objects.all()
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class added successfully!')
            return redirect('manage_classes')
    else:
        form = ClassForm()
    return render(request, 'core/manage_classes.html', {'form': form, 'classes': classes})

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_divisions(request):
    divisions = Division.objects.all()
    if request.method == 'POST':
        form = DivisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Division added successfully!')
            return redirect('manage_divisions')
    else:
        form = DivisionForm()
    return render(request, 'core/manage_divisions.html', {'form': form, 'divisions': divisions})

@login_required
@user_passes_test(lambda u: u.is_staff)
def student_mark_entry(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    section = student.class_section
    subjects = section.subjects.all()
    exams = Exam.objects.all()
    selected_exam_id = request.GET.get('exam') or request.POST.get('exam')
    selected_exam = None
    if selected_exam_id:
        selected_exam = get_object_or_404(Exam, pk=selected_exam_id)
    form = None
    if selected_exam:
        if request.method == 'POST':
            form = StudentMarksEntryForm(subjects, request.POST)
            if form.is_valid():
                for subject in subjects:
                    marks = form.cleaned_data.get(f'subject_{subject.pk}')
                    if marks is not None:
                        Mark.objects.update_or_create(
                            student=student,
                            exam=selected_exam,
                            subject=subject,
                            defaults={'marks_obtained': marks}
                        )
                messages.success(request, 'Marks saved successfully.')
                return redirect('section_marks_entry', section_id=section.pk)
        else:
            form = StudentMarksEntryForm(subjects)
    return render(request, 'core/student_mark_entry.html', {
        'student': student,
        'form': form,
        'selected_exam': selected_exam,
        'exams': exams,
    })