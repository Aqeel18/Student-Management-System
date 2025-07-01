from django import forms
from .models import Student, Exam, Subject, SchoolClass, Division, ClassDivision, Mark

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

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'date', 'academic_year']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'roll_number', 'class_division', 'id_number', 'phone_number', 'address', 'alternate_email', 'profile_photo']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'subjects']

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['name']

class ClassDivisionForm(forms.ModelForm):
    class Meta:
        model = ClassDivision
        fields = ['student_class', 'division']

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'subject', 'exam', 'marks_obtained']
