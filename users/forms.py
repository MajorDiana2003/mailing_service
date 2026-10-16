from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации строго по Email без username"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)


class CustomAuthenticationForm(AuthenticationForm):
    """Форма для авторизации строго по Email"""
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
