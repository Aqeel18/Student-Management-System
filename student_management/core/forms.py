from django import forms
from django.contrib.auth.models import User
from .models import Student, Exam, Subject, Division, Mark, ClassSection, Teacher, Class

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'roll_number', 'class_section', 'profile_photo',
            'date_of_birth', 'address', 'phone', 'guardian_name', 'guardian_phone'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'cols': 40, 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields.pop('user')

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'date']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['name']

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'exam', 'subject', 'marks_obtained']

class ClassSectionForm(forms.ModelForm):
    class Meta:
        model = ClassSection
        fields = ['school_class', 'division', 'teacher', 'subjects']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple,
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email']

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name']

class StudentProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'class_section', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        student = super().save(commit=False)
        user = student.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            student.save()
        return student

class StudentMarksEntryForm(forms.Form):
    def __init__(self, subjects, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for subject in subjects:
            self.fields[f'subject_{subject.pk}'] = forms.FloatField(
                label=subject.name,
                required=False,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter marks'})
            )
