from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Student, Mark, Exam, Subject, SchoolClass, Division, ClassDivision
from .forms import StudentProfileForm, ExamForm, StudentForm, SubjectForm, SchoolClassForm, DivisionForm, ClassDivisionForm, MarkForm
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

def custom_logout_view(request):
    is_staff = request.user.is_staff
    logout(request)
    
    if is_staff:
        return redirect('/admin/login/')
    else:
        return redirect('/accounts/login/')



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


class AdminLoginView(View):
    template_name = 'registration/admin_login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')
            return render(request, self.template_name)


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


@method_decorator(admin_required, name='dispatch')
class ExamListView(ListView):
    model = Exam
    template_name = 'core/exam_list.html'
    context_object_name = 'exams'

@method_decorator(admin_required, name='dispatch')
class ExamCreateView(CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'core/exam_form.html'
    success_url = reverse_lazy('manage-exams')

@method_decorator(admin_required, name='dispatch')
class ExamUpdateView(UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'core/exam_form.html'
    success_url = reverse_lazy('manage-exams')

@method_decorator(admin_required, name='dispatch')
class ExamDeleteView(DeleteView):
    model = Exam
    template_name = 'core/exam_confirm_delete.html'
    success_url = reverse_lazy('manage-exams')


@method_decorator(admin_required, name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'core/student_list.html'
    context_object_name = 'students'

@method_decorator(admin_required, name='dispatch')
class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'core/student_form.html'
    success_url = reverse_lazy('manage-students')

@method_decorator(admin_required, name='dispatch')
class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'core/student_form.html'
    success_url = reverse_lazy('manage-students')

@method_decorator(admin_required, name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'core/student_confirm_delete.html'
    success_url = reverse_lazy('manage-students')

@method_decorator(admin_required, name='dispatch')
class SubjectListView(ListView):
    model = Subject
    template_name = 'core/subject_list.html'
    context_object_name = 'subjects'

@method_decorator(admin_required, name='dispatch')
class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'core/subject_form.html'
    success_url = reverse_lazy('manage-subjects')

@method_decorator(admin_required, name='dispatch')
class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'core/subject_form.html'
    success_url = reverse_lazy('manage-subjects')

@method_decorator(admin_required, name='dispatch')
class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'core/subject_confirm_delete.html'
    success_url = reverse_lazy('manage-subjects')

@method_decorator(admin_required, name='dispatch')
class SchoolClassListView(ListView):
    model = SchoolClass
    template_name = 'core/schoolclass_list.html'
    context_object_name = 'classes'

@method_decorator(admin_required, name='dispatch')
class SchoolClassCreateView(CreateView):
    model = SchoolClass
    form_class = SchoolClassForm
    template_name = 'core/schoolclass_form.html'
    success_url = reverse_lazy('manage-classes')

@method_decorator(admin_required, name='dispatch')
class SchoolClassUpdateView(UpdateView):
    model = SchoolClass
    form_class = SchoolClassForm
    template_name = 'core/schoolclass_form.html'
    success_url = reverse_lazy('manage-classes')

@method_decorator(admin_required, name='dispatch')
class SchoolClassDeleteView(DeleteView):
    model = SchoolClass
    template_name = 'core/schoolclass_confirm_delete.html'
    success_url = reverse_lazy('manage-classes')

@method_decorator(admin_required, name='dispatch')
class DivisionListView(ListView):
    model = Division
    template_name = 'core/division_list.html'
    context_object_name = 'divisions'

@method_decorator(admin_required, name='dispatch')
class DivisionCreateView(CreateView):
    model = Division
    form_class = DivisionForm
    template_name = 'core/division_form.html'
    success_url = reverse_lazy('manage-divisions')

@method_decorator(admin_required, name='dispatch')
class DivisionUpdateView(UpdateView):
    model = Division
    form_class = DivisionForm
    template_name = 'core/division_form.html'
    success_url = reverse_lazy('manage-divisions')

@method_decorator(admin_required, name='dispatch')
class DivisionDeleteView(DeleteView):
    model = Division
    template_name = 'core/division_confirm_delete.html'
    success_url = reverse_lazy('manage-divisions')

@method_decorator(admin_required, name='dispatch')
class ClassDivisionListView(ListView):
    model = ClassDivision
    template_name = 'core/classdivision_list.html'
    context_object_name = 'classdivisions'

@method_decorator(admin_required, name='dispatch')
class ClassDivisionCreateView(CreateView):
    model = ClassDivision
    form_class = ClassDivisionForm
    template_name = 'core/classdivision_form.html'
    success_url = reverse_lazy('manage-classdivisions')

@method_decorator(admin_required, name='dispatch')
class ClassDivisionUpdateView(UpdateView):
    model = ClassDivision
    form_class = ClassDivisionForm
    template_name = 'core/classdivision_form.html'
    success_url = reverse_lazy('manage-classdivisions')

@method_decorator(admin_required, name='dispatch')
class ClassDivisionDeleteView(DeleteView):
    model = ClassDivision
    template_name = 'core/classdivision_confirm_delete.html'
    success_url = reverse_lazy('manage-classdivisions')

@method_decorator(admin_required, name='dispatch')
class MarkListView(ListView):
    model = Mark
    template_name = 'core/mark_list.html'
    context_object_name = 'marks'

@method_decorator(admin_required, name='dispatch')
class MarkCreateView(CreateView):
    model = Mark
    form_class = MarkForm
    template_name = 'core/mark_form.html'
    success_url = reverse_lazy('marks-entry')

@method_decorator(admin_required, name='dispatch')
class MarkUpdateView(UpdateView):
    model = Mark
    form_class = MarkForm
    template_name = 'core/mark_form.html'
    success_url = reverse_lazy('marks-entry')

@method_decorator(admin_required, name='dispatch')
class MarkDeleteView(DeleteView):
    model = Mark
    template_name = 'core/mark_confirm_delete.html'
    success_url = reverse_lazy('marks-entry')