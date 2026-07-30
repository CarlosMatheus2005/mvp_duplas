import django_filters
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Avaliacao, Comodidade, Imovel, Reserva
from .permissions import EhAnfitriaoDaReserva, EhDonoDoImovelOuSomenteLeitura, EhHospedeDaReserva
from .serializers import (
    AvaliacaoSerializer,
    ComodidadeSerializer,
    ImovelDetailSerializer,
    ImovelListSerializer,
    ReservaSerializer,
    ReservaStatusSerializer,
)


class ComodidadeListView(generics.ListAPIView):
    queryset = Comodidade.objects.all()
    serializer_class = ComodidadeSerializer
    permission_classes = [permissions.AllowAny]

class ImovelFilter(django_filters.FilterSet):
    cidade = django_filters.CharFilter(field_name='cidade', lookup_expr='icontains')
    preco_min = django_filters.NumberFilter(field_name='preco_diaria', lookup_expr='gte')
    preco_max = django_filters.NumberFilter(field_name='preco_diaria', lookup_expr='lte')
    hospedes = django_filters.NumberFilter(field_name='capacidade_maxima', lookup_expr='gte')
    class Meta:
        model = Imovel
        fields = ['cidade', 'preco_min', 'preco_max', 'hospedes']


class ImovelViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
      GET    /api/imoveis/                  -> listar (com filtros)
      GET    /api/imoveis/{id}/              -> detalhe
      POST   /api/imoveis/                   -> cadastrar (autenticado)
      PUT/PATCH /api/imoveis/{id}/           -> editar (só o dono)
      DELETE /api/imoveis/{id}/              -> remover (só o dono)
      GET    /api/imoveis/meus/              -> meus imóveis (como anfitrião)
      GET    /api/imoveis/{id}/calendario/   -> dias já reservados
      GET    /api/imoveis/{id}/avaliacoes/   -> avaliações do imóvel
    """

    queryset = Imovel.objects.all()
    permission_classes = [EhDonoDoImovelOuSomenteLeitura]
    filterset_class = ImovelFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return ImovelListSerializer
        return ImovelDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio and data_fim:
            reservados = Reserva.objects.filter(
                status__in=[Reserva.Status.PENDENTE, Reserva.Status.APROVADA],
                data_inicio__lt=data_fim,
                data_fim__gt=data_inicio,
            ).values_list('imovel_id', flat=True)
            queryset = queryset.exclude(id__in=reservados)

        return queryset

    def get_permissions(self):
        if self.action == 'meus':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_destroy(self, instance):
        if instance.anfitriao_id != self.request.user.id:
            raise PermissionDenied('Você só pode remover imóveis que você mesmo cadastrou.')
        instance.delete()

    @action(detail=False, methods=['get'])
    def meus(self, request):
        """GET /api/imoveis/meus/ - lista os imóveis cadastrados pelo usuário logado."""
        imoveis = Imovel.objects.filter(anfitriao=request.user)
        serializer = ImovelListSerializer(imoveis, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def calendario(self, request, pk=None):
        """GET /api/imoveis/{id}/calendario/ - períodos já pendentes/aprovados para este imóvel."""
        imovel = self.get_object()
        reservas = imovel.reservas.filter(
            status__in=[Reserva.Status.PENDENTE, Reserva.Status.APROVADA]
        ).values('data_inicio', 'data_fim', 'status')
        return Response(list(reservas))

    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):
        """GET /api/imoveis/{id}/avaliacoes/ - lista as avaliações recebidas por este imóvel."""
        imovel = self.get_object()
        serializer = AvaliacaoSerializer(imovel.avaliacoes.all(), many=True, context={'request': request})
        return Response(serializer.data)

class ReservaCreateView(generics.CreateAPIView):
    """POST /api/reservas/ - hóspede solicita uma reserva."""
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}


class MinhasReservasView(generics.ListAPIView):
    """GET /api/reservas/minhas/ - reservas que EU fiz como hóspede."""
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reserva.objects.filter(hospede=self.request.user)


class ReservasRecebidasView(generics.ListAPIView):
    """GET /api/reservas/recebidas/ - reservas recebidas nos MEUS imóveis (como anfitrião)."""
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reserva.objects.filter(imovel__anfitriao=self.request.user)


class ReservaStatusView(generics.UpdateAPIView):
    """PATCH /api/reservas/{id}/status/ - anfitrião aprova ou recusa a solicitação."""
    queryset = Reserva.objects.all()
    serializer_class = ReservaStatusSerializer
    permission_classes = [permissions.IsAuthenticated, EhAnfitriaoDaReserva]

class AvaliacaoCreateView(generics.CreateAPIView):
    """POST /api/avaliacoes/ - cria uma avaliação vinculada a uma reserva concluída."""
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
