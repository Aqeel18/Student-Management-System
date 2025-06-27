from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # 👈 your homepage
    path('profile/', views.student_profile_view, name='student-profile'),
]
