
from django.contrib import admin
from django.urls import path, include
from tasks.views import manager_dashboard, user_dashboard


urlpatterns = [
    path('admin/', admin.site.urls),
    path('manager-dashboard/', manager_dashboard),
    path('user-dashboard/', user_dashboard),
    path('test/', include('tasks.urls'))  # Assuming you want to include the test view from tasks.urls
]
