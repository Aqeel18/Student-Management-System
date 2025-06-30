from django.urls import path
from .views import home_view, student_profile_view, custom_logout_view, student_results

urlpatterns = [
    path('', home_view, name='home'),
    path('profile/', student_profile_view, name='student-profile'),
    path('results/', student_results, name='student-results'),
    path('logout/', custom_logout_view, name='logout'),  # 👈 Custom logout route
]
