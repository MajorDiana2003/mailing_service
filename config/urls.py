from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Ссылки пользователей будут доступны по адресу http://127.0.0...
    path('users/', include('users.urls', namespace='users')),
    # Управление рассылками
    path('', include('mailing.urls', namespace='mailing')),
]
