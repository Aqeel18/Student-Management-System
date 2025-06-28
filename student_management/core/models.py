from django.db import models
from django.contrib.auth.models import User

# === Class & Division ===

class Class(models.Model):
    name = models.CharField(max_length=20)  # e.g., "10th", "11th"

    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=2)  # e.g., "A", "B"

    def __str__(self):
        return self.name

class ClassDivision(models.Model):
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student_class', 'division')

    def __str__(self):
        return f"{self.student_class.name}{self.division.name}"

# === Subjects ===

class Subject(models.Model):
    name = models.CharField(max_length=100)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.student_class})"

class DivisionSubject(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_division = models.ForeignKey(ClassDivision, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('subject', 'class_division')

    def __str__(self):
        return f"{self.subject.name} - {self.class_division}"

# === Student ===

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    class_division = models.ForeignKey(ClassDivision, on_delete=models.SET_NULL, null=True)
    id_number = models.CharField(max_length=20, unique=True)

    # Personal details
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    alternate_email = models.EmailField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    class Meta:
        unique_together = ('roll_number', 'class_division')  # ✅ ENFORCES uniqueness within division

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.class_division}"

# === Exams & Marks ===

class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    academic_year = models.CharField(max_length=9)  # e.g., "2024-2025"

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()

    class Meta:
        unique_together = ('student', 'subject', 'exam')

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.exam}: {self.marks_obtained}"
