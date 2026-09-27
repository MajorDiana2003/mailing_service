from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    # Главная страница со статистикой теперь открывается первой
    path('', views.IndexView.as_view(), name='index'),

    # Список рассылок теперь доступен по адресу http://127.0.0
    path('mailings/', views.MailingListView.as_view(), name='list'),
    path('create/', views.MailingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MailingDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.MailingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.MailingDeleteView.as_view(), name='delete'),
    path('<int:pk>/trigger/', views.trigger_mailing_view, name='trigger'),
]
