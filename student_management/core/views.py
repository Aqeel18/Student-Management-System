from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Student
from .forms import StudentProfileForm

@login_required
def student_profile_view(request):
    try:
        student = request.user.student  # Get student linked to logged-in user
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')  # Change this to your actual home view name

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student-profile')  # This name we'll set in urls.py
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'core/student_profile.html', {
        'form': form,
        'student': student,
    })

