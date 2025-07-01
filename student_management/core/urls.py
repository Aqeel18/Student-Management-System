from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('profile/', student_profile_view, name='student-profile'),
    path('results/', student_results, name='student-results'),
    path('logout/', custom_logout_view, name='logout'),  # 👈 Custom logout route
    path('login/', StudentLoginView.as_view(), name='login'),
    path('dashboard/', index , name='dashboard'),  # 👈 Added index route
    path('base/', base, name='base'),  # 👈 Added base route
    path('manage-students/', StudentListView.as_view(), name='manage-students'),
    path('manage-students/add/', StudentCreateView.as_view(), name='add-student'),
    path('manage-students/<int:pk>/edit/', StudentUpdateView.as_view(), name='edit-student'),
    path('manage-students/<int:pk>/delete/', StudentDeleteView.as_view(), name='delete-student'),

    path('manage-exams/', ExamListView.as_view(), name='manage-exams'),
    path('manage-exams/add/', ExamCreateView.as_view(), name='add-exam'),
    path('manage-exams/<int:pk>/edit/', ExamUpdateView.as_view(), name='edit-exam'),
    path('manage-exams/<int:pk>/delete/', ExamDeleteView.as_view(), name='delete-exam'),

    path('manage-subjects/', SubjectListView.as_view(), name='manage-subjects'),
    path('manage-subjects/add/', SubjectCreateView.as_view(), name='add-subject'),
    path('manage-subjects/<int:pk>/edit/', SubjectUpdateView.as_view(), name='edit-subject'),
    path('manage-subjects/<int:pk>/delete/', SubjectDeleteView.as_view(), name='delete-subject'),

    path('manage-classes/', SchoolClassListView.as_view(), name='manage-classes'),
    path('manage-classes/add/', SchoolClassCreateView.as_view(), name='add-class'),
    path('manage-classes/<int:pk>/edit/', SchoolClassUpdateView.as_view(), name='edit-class'),
    path('manage-classes/<int:pk>/delete/', SchoolClassDeleteView.as_view(), name='delete-class'),

    path('manage-divisions/', DivisionListView.as_view(), name='manage-divisions'),
    path('manage-divisions/add/', DivisionCreateView.as_view(), name='add-division'),
    path('manage-divisions/<int:pk>/edit/', DivisionUpdateView.as_view(), name='edit-division'),
    path('manage-divisions/<int:pk>/delete/', DivisionDeleteView.as_view(), name='delete-division'),

    path('manage-classdivisions/', ClassDivisionListView.as_view(), name='manage-classdivisions'),
    path('manage-classdivisions/add/', ClassDivisionCreateView.as_view(), name='add-classdivision'),
    path('manage-classdivisions/<int:pk>/edit/', ClassDivisionUpdateView.as_view(), name='edit-classdivision'),
    path('manage-classdivisions/<int:pk>/delete/', ClassDivisionDeleteView.as_view(), name='delete-classdivision'),

    path('marks-entry/', MarkListView.as_view(), name='marks-entry'),
    path('marks-entry/add/', MarkCreateView.as_view(), name='add-mark'),
    path('marks-entry/<int:pk>/edit/', MarkUpdateView.as_view(), name='edit-mark'),
    path('marks-entry/<int:pk>/delete/', MarkDeleteView.as_view(), name='delete-mark'),

    path('bulk-upload/', bulk_upload_view, name='bulk-upload'),
    path('id-card-generator/', id_card_generator_view, name='id-card-generator'),
    path('reports/', reports_view, name='reports'),

    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
]
