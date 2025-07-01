from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SchoolClass, Subject, Student, Exam, ClassDivision, Division

class Command(BaseCommand):
    help = 'Create demo data: class, subjects, student, exam, and link them.'

    def handle(self, *args, **kwargs):
        # Create class
        school_class, _ = SchoolClass.objects.get_or_create(name="10th")
        # Create subjects
        math, _ = Subject.objects.get_or_create(name="Math", student_class=school_class)
        science, _ = Subject.objects.get_or_create(name="Science", student_class=school_class)
        english, _ = Subject.objects.get_or_create(name="English", student_class=school_class)
        # Link subjects to class (many-to-many)
        school_class.subjects.set([math, science, english])
        # Create division
        division, _ = Division.objects.get_or_create(name="A")
        class_div, _ = ClassDivision.objects.get_or_create(student_class=school_class, division=division)
        # Create user and student
        user, _ = User.objects.get_or_create(username="student1", defaults={"first_name": "Test", "last_name": "Student"})
        student, _ = Student.objects.get_or_create(user=user, roll_number="1", class_division=class_div, id_number="S1001")
        # Create exam
        exam, _ = Exam.objects.get_or_create(name="Midterm", academic_year="2024-2025", date="2025-06-01")
        self.stdout.write(self.style.SUCCESS("Demo data created! You can now use the bulk marks entry form in the admin."))
