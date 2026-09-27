from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import MailingAttempt


def send_mailing_manually(mailing):
    """
    Функция для обработки и ручного запуска конкретной рассылки.
    Проверяет время, шлёт письма клиентам и логирует попытки через batch.
    """
    now = timezone.now()

    # 1. Валидация времени вызова (строго по критериям ТЗ из скриншота)
    if not (mailing.start_time <= now <= mailing.end_time):
        raise ValueError("Отправка запрещена: текущее время не входит в разрешенный интервал рассылки.")

    # Список, куда мы будем временно складывать объекты попыток
    attempts_to_create = []

    # 2. Определение получателей и отправка писем для каждого клиента
    for recipient in mailing.recipients.all():
        try:
            # Встроенная функция Django для отправки почты
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient.email],
                fail_silently=False,  # Если будет ошибка — мы её поймаем в except
            )
            # Если письмо ушло успешно, готовим запись для лога
            attempts_to_create.append(
                MailingAttempt(
                    mailing=mailing,
                    status='Успешно',
                    server_response='Письмо успешно доставлено почтовым сервером.'
                )
            )
        except Exception as e:
            # Если произошёл сбой (например, нет интернета или неверный пароль от почты)
            attempts_to_create.append(
                MailingAttempt(
                    mailing=mailing,
                    status='Не успешно',
                    server_response=str(e)
                )
            )

    if attempts_to_create:
        MailingAttempt.objects.bulk_create(attempts_to_create)

    # Динамически пересчитываем статус рассылки после завершения процесса
    mailing.update_status()
