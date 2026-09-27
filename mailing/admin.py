from django.contrib import admin
from .models import Recipient, Message, Mailing, MailingAttempt


# Настраиваем отображение получателей в таблице
@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'owner')
    search_fields = ('name', 'email')


# Настраиваем отображение сообщений
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'owner')
    search_fields = ('subject', 'body')


# Настраиваем отображение рассылок
@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'is_active', 'owner')
    list_filter = ('status', 'is_active')


# Настраиваем отображение логов/попыток отправки
@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_time', 'status', 'mailing')
    list_filter = ('status',)
