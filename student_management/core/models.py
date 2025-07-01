from django.db import models
from django.contrib.auth.models import User

# === SchoolClass & Division ===

class Class(models.Model):
    name = models.CharField(max_length=20)  # e.g., "10", "12"

    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=2)  # e.g., "A", "B"

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class ClassSection(models.Model):
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    subjects = models.ManyToManyField('Subject', blank=True, related_name='class_sections')

    def __str__(self):
        return f"{self.school_class.name}{self.division.name}"

# === Subjects ===

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# === Student ===

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.roll_number} - {self.name}"

# === Exams & Marks ===

class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.marks_obtained}"
