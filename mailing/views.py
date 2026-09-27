
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MailingForm
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Mailing, Recipient
from .services import send_mailing_manually


# 1. Список всех рассылок
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        """Фильтруем список: суперпользователь и персонал видят всё, обычный юзер — только своё"""
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.is_staff:
            return queryset
        return queryset.filter(owner=self.request.user)


# 2. Детальная информация о рассылке (с автоматическим пересчетом статуса)
class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_object(self, queryset=None):
        """Переопределяем метод: при каждом открытии страницы статус пересчитывается"""
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


# 3. Создание новой рассылки
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:list')

    def form_valid(self, form):
        """Автоматически назначаем текущего пользователя владельцем рассылки"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


# 4. Редактирование рассылки
class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def get_success_url(self):
        return reverse('mailing:detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        """Проверка: редактировать может только хозяин или суперадмин"""
        obj = self.get_object()
        return self.request.user == obj.owner or self.request.user.is_superuser


# 5. Удаление рассылки
class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:list')

    def test_func(self):
        """Проверка: удалять может только хозяин или суперадмин"""
        obj = self.get_object()
        return self.request.user == obj.owner or self.request.user.is_superuser


# 6. Кнопка ручного запуска рассылки из интерфейса (Экшен)
def trigger_mailing_view(request, pk):
    """Специальный контроллер-функция для ручного запуска отправки писем"""
    mailing = get_object_or_404(Mailing, pk=pk)
    try:
        send_mailing_manually(mailing)
        messages.success(request, "Рассылка успешно выполнена! Логи записаны в базу.")
    except ValueError as e:
        # Если время рассылки еще не пришло или уже прошло, выведется ошибка
        messages.error(request, str(e))

    return redirect('mailing:detail', pk=pk)


class IndexView(TemplateView):
    """Контроллер главной страницы со статистикой"""
    template_name = 'mailing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Подсчитываем данные по всей системе
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='Запущена', is_active=True).count()

        # Считаем количество уникальных email-адресов клиентов
        context['unique_recipients'] = Recipient.objects.values('email').distinct().count()

        return context
