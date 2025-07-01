from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.views import AdminLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),  # Custom admin login FIRST
    path('grappelli/', include('grappelli.urls')),  # Grappelli admin interface
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # For login/logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
