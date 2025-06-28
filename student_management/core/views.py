from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Student, Mark
from .forms import StudentProfileForm
from django.contrib.auth import logout

def custom_logout_view(request):
    is_staff = request.user.is_staff
    logout(request)
    
    if is_staff:
        return redirect('/admin/login/')
    else:
        return redirect('/accounts/login/')



@login_required
def home_view(request):
    # ✅ If the user is admin/staff, redirect to the Django admin panel
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')  # Or: reverse('admin:index')

    # ✅ Try to load the student's dashboard
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return HttpResponse("Student profile not found. Please contact the administrator.")

    # ✅ Fetch marks grouped by exam
    marks = Mark.objects.filter(student=student).select_related('exam', 'subject')

    exam_results = {}
    for mark in marks:
        exam = mark.exam
        if exam not in exam_results:
            exam_results[exam] = []
        exam_results[exam].append(mark)

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
