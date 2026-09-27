from django import forms
from mailing.models import Mailing, Message, Recipient  # Добавили импорт Message и Recipient


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "periodic", "message", "recipients"]

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(
                attrs={"class": "form-select", "style": "height: 120px;"}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем пользователя, переданного из контроллера (views.py)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Если пользователь передан и он не суперпользователь/менеджер, изолируем данные
        if user and not (user.is_superuser or user.is_staff):
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)

