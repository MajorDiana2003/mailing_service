from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Настройки отображения пользователей в админке
    list_display = ('id', 'email', 'is_verified', 'is_staff', 'is_active')
    ordering = ('email',)

    # Так как мы убрали username, нужно перенастроить стандартные поля формы админки
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'verification_token')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password'),
        }),
    )
