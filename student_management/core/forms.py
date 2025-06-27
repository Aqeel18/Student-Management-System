from django import forms
from .models import Student

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'phone_number',
            'address',
            'alternate_email',
            'profile_photo',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
