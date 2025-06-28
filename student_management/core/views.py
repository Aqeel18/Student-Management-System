from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Student, Mark
from .forms import StudentProfileForm
from django.contrib.auth import logout
from django.views.decorators.http import require_POST

@login_required
@require_POST
def custom_logout_view(request):
    # NOTE: This view should only be used for student logout (not admin logout).
    is_staff = request.user.is_staff or request.user.is_superuser
    logout(request)
    if is_staff:
        return redirect('/admin/login/?next=/admin/')
    else:
        return redirect('/accounts/login/')



@login_required
def home_view(request):
    # ✅ Always show the home page, regardless of user type
    try:
        student = request.user.student
    except Student.DoesNotExist:
        # Optionally, show a different page for staff/superuser
        if request.user.is_staff or request.user.is_superuser:
            return HttpResponse("Welcome, admin user. No student profile is associated with your account.")
        return HttpResponse("Student profile not found. Please contact the administrator.")

    # ✅ Fetch marks grouped by exam
    marks = Mark.objects.filter(student=student).select_related('exam', 'subject')

    exam_results = {}
    for mark in marks:
        exam_name = mark.exam.name
        if exam_name not in exam_results:
            exam_results[exam_name] = []
        exam_results[exam_name].append(mark)

    return render(request, 'core/student_dashboard.html', {
        'student': student,
        'exam_results': exam_results,
    })


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
