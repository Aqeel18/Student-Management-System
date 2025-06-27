from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import Student
from .forms import StudentProfileForm

def home_view(request):
    return render(request, 'core/home.html')
@login_required
def student_profile_view(request):
    try:
        # Try to get the Student object linked to the logged-in user
        student = request.user.student
    except Student.DoesNotExist:
        # Instead of redirecting to self, show an error message
        return HttpResponse("Student profile not found. Please contact the administrator.")

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student-profile')  # Redirect back to the same page
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'core/student_profile.html', {
        'form': form,
        'student': student,
    })
