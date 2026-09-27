from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings


class Recipient(models.Model):
    """Модель получателя рассылки (наши клиенты)"""
    email = models.EmailField(unique=True, verbose_name="Email получателя")
    name = models.CharField(max_length=150, verbose_name="Имя")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    # Каждый клиент привязан к создавшему его пользователю (ТЗ: Ограничение доступа)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name="Владелец", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"


class Message(models.Model):
    """Модель сообщения для рассылки"""
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    # Каждое сообщение тоже принадлежит конкретному пользователю
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name="Владелец", null=True, blank=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    """Модель самой рассылки"""
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущен'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана', verbose_name="Статус")

    # Связи с другими моделями
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipient, verbose_name="Получатели (клиенты)")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name="Владелец рассылки", null=True, blank=True)

    # Флаг для менеджера, чтобы он мог принудительно отключать чужие рассылки по ТЗ
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def clean(self):
        """Валидация дат перед сохранением в базу данных"""
        super().clean()

        # Проверяем, что обе даты вообще заполнены и распознаны системой
        if not self.start_time or not self.end_time:
            raise ValidationError("Пожалуйста, введите корректные дату и время.")

        # 1. Время начала не может быть в прошлом
        if not self.pk and self.start_time < timezone.now():
            raise ValidationError({'start_time': "Дата и время начала не могут быть в прошлом."})

        # 2. Время начала должно быть раньше времени окончания
        if self.start_time >= self.end_time:
            raise ValidationError({'end_time': "Дата окончания должна быть строго позже даты начала."})

    def update_status(self):
        """Динамический пересчет статуса (как просили в ТЗ)"""
        now = timezone.now()

        # Если менеджер деактивировал рассылку, мы её не пересчитываем автоматически
        if not self.is_active:
            return

        new_status = self.status
        if now < self.start_time:
            new_status = 'Создана'
        elif self.start_time <= now <= self.end_time:
            new_status = 'Запущена'
        else:
            new_status = 'Завершена'

        # Сохраняем в базу только если статус действительно поменялся
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Рассылка #{self.pk} (Статус: {self.status})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingAttempt(models.Model):
    """Модель попыток рассылок (Логирование строго по ТЗ)"""
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ почтового сервера")

    # Внешний ключ на саму рассылку
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
