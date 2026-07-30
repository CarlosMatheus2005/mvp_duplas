from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, MeuPerfilView, RegistroView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='usuario-registro'),
    path('login/', LoginView.as_view(), name='usuario-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', MeuPerfilView.as_view(), name='usuario-me'),
]
