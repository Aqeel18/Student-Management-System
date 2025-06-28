from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin handles its own logout
    path('accounts/logout/', core_views.custom_logout_view, name='custom_logout'),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # For login/logout
]

# 👇 Add this block at the very bottom
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
