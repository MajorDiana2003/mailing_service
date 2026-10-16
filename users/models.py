from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для управления пользователями (нужен, так как мы волнообразно убрали username)"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя по требованиям ТЗ"""
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')

    # Поля для подтверждения регистрации по почте
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    verification_token = models.CharField(max_length=100, blank=True, null=True, verbose_name='Токен верификации')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
