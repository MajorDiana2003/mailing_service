from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verification-sent/', views.VerificationSentView.as_view(), name='verification_sent'),
    path('verify/<str:token>/', views.verify_email_view, name='verify'),
]
