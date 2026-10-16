import secrets
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.conf import settings

from .models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class CustomLoginView(LoginView):
    """Контроллер входа на сайт"""
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'


class CustomLogoutView(LogoutView):
    """Контроллер выхода с сайта"""
    next_page = reverse_lazy('mailing:list')


class RegisterView(CreateView):
    """Контроллер регистрации нового аккаунта с генерацией токена"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:verification_sent')

    def form_valid(self, form):
        # Сохраняем пользователя, но пока деактивируем его
        user = form.save(commit=False)
        user.is_active = False
        user.is_verified = False

        # Генерируем уникальный случайный токен безопасности
        token = secrets.token_hex(16)
        user.verification_token = token
        user.save()

        # Формируем ссылку для подтверждения
        # Ссылка будет иметь вид: http://127.0.0
        host = self.request.get_host()
        verify_url = f"http://{host}{reverse('users:verify', kwargs={'token': token})}"

        # Отправляем письмо с токеном
        send_mail(
            subject="Подтверждение регистрации на сервисе рассылок",
            message=f"Здравствуйте! Для активации вашего аккаунта перейдите по ссылке: {verify_url}",
            from_email=settings.EMAIL_CONFIG.get('EMAIL_HOST_USER', 'test@example.com'),
            recipient_list=[user.email],
            fail_silently=False,
        )

        return super().form_valid(form)


class VerificationSentView(TemplateView):
    """Простая страница с текстом 'Проверьте почту'"""
    template_name = 'users/verification_sent.html'


def verify_email_view(request, token):
    """Контроллер, который срабатывает, когда пользователь кликает по ссылке из письма"""
    try:
        # Ищем пользователя с таким токеном в базе
        user = User.objects.get(verification_token=token)
        user.is_active = True  # Активируем аккаунт
        user.is_verified = True  # Ставим галочку верификации
        user.verification_token = None  # Стираем токен, так как он больше не нужен
        user.save()
        return render(request, 'users/login.html', {
            'form': CustomAuthenticationForm(),
            'success_message': 'Ваш аккаунт успешно активирован! Теперь вы можете войти.'
        })
    except User.DoesNotExist:
        # Если токен поддельный или устарел
        return render(request, 'users/login.html', {
            'form': CustomAuthenticationForm(),
            'error_message': 'Ссылка для активации недействительна или устарела.'
        })
