from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvaliacaoCreateView,
    ComodidadeListView,
    ImovelViewSet,
    MinhasReservasView,
    ReservaCreateView,
    ReservaStatusView,
    ReservasRecebidasView,
)

router = DefaultRouter()
router.register('imoveis', ImovelViewSet, basename='imovel')

urlpatterns = [
    path('', include(router.urls)),

    path('comodidades/', ComodidadeListView.as_view(), name='comodidade-list'),

    path('reservas/', ReservaCreateView.as_view(), name='reserva-create'),
    path('reservas/minhas/', MinhasReservasView.as_view(), name='reserva-minhas'),
    path('reservas/recebidas/', ReservasRecebidasView.as_view(), name='reserva-recebidas'),
    path('reservas/<int:pk>/status/', ReservaStatusView.as_view(), name='reserva-status'),

    path('avaliacoes/', AvaliacaoCreateView.as_view(), name='avaliacao-create'),
]
