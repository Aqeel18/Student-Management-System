from django.urls import path
from .views import home_view, student_profile_view, custom_logout_view

urlpatterns = [
    path('', home_view, name='home'),
    path('profile/', student_profile_view, name='student-profile'),
    path('logout/', custom_logout_view, name='logout'),  # 👈 Custom logout route
]
