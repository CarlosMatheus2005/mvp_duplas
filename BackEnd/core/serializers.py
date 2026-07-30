from django.utils import timezone
from rest_framework import serializers

from .models import Avaliacao, Comodidade, ImagemImovel, Imovel, Reserva


class ComodidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comodidade
        fields = ['id', 'nome', 'icone']

class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        fields = ['id', 'imagem', 'ordem']

class AvaliacaoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Avaliacao
        fields = [
            'id', 'imovel', 'usuario', 'reserva',
            'nota', 'descricao_avaliacao', 'data_criacao',
        ]
        read_only_fields = ['id', 'imovel', 'usuario', 'data_criacao']

    def validate_reserva(self, reserva):
        usuario = self.context['request'].user

        if reserva.hospede_id != usuario.id:
            raise serializers.ValidationError('Você só pode avaliar usando uma reserva feita por você.')

        if reserva.status != Reserva.Status.APROVADA:
            raise serializers.ValidationError('Só é possível avaliar reservas aprovadas/concluídas.')

        if hasattr(reserva, 'avaliacao'):
            raise serializers.ValidationError('Esta reserva já possui uma avaliação.')

        return reserva

    def create(self, validated_data):
        # O imóvel é sempre o mesmo da reserva, e o usuário é o hóspede logado
        reserva = validated_data['reserva']
        validated_data['imovel'] = reserva.imovel
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

class ImovelListSerializer(serializers.ModelSerializer):

    nota_media = serializers.FloatField(read_only=True)
    imagem_capa = serializers.SerializerMethodField()

    class Meta:
        model = Imovel
        fields = [
            'id', 'titulo', 'cidade', 'preco_diaria',
            'capacidade_maxima', 'nota_media', 'imagem_capa',
        ]

    def get_imagem_capa(self, obj):
        primeira_imagem = obj.imagens.first()
        if primeira_imagem:
            request = self.context.get('request')
            url = primeira_imagem.imagem.url
            return request.build_absolute_uri(url) if request else url
        return None


class ImovelDetailSerializer(serializers.ModelSerializer):

    anfitriao = serializers.StringRelatedField(read_only=True)
    imagens = ImagemImovelSerializer(many=True, read_only=True)
    nota_media = serializers.FloatField(read_only=True)

    comodidades = serializers.PrimaryKeyRelatedField(
        queryset=Comodidade.objects.all(), many=True, required=False
    )

    class Meta:
        model = Imovel
        fields = [
            'id', 'anfitriao', 'titulo', 'descricao',
            'endereco', 'cidade', 'cep', 'latitude', 'longitude',
            'capacidade_maxima', 'preco_diaria',
            'comodidades', 'imagens', 'nota_media', 'data_criacao',
        ]
        read_only_fields = ['id', 'anfitriao', 'data_criacao']

    def create(self, validated_data):
        # O anfitrião é sempre o usuário autenticado que está fazendo a requisição
        validated_data['anfitriao'] = self.context['request'].user
        return super().create(validated_data)


class ReservaSerializer(serializers.ModelSerializer):
    hospede = serializers.StringRelatedField(read_only=True)
    imovel_titulo = serializers.CharField(source='imovel.titulo', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'imovel', 'imovel_titulo', 'hospede',
            'data_inicio', 'data_fim', 'status',
            'valor_total', 'forma_pagamento', 'data_criacao',
        ]
        read_only_fields = ['id', 'hospede', 'status', 'valor_total', 'data_criacao']

    def validate(self, dados):
        imovel = dados['imovel']
        inicio = dados['data_inicio']
        fim = dados['data_fim']

        if fim <= inicio:
            raise serializers.ValidationError('A data de término deve ser posterior à data de início.')

        if inicio < timezone.localdate():
            raise serializers.ValidationError('Não é possível reservar em uma data que já passou.')

        # Verifica conflito com reservas já pendentes/aprovadas do mesmo imóvel
        conflito = Reserva.objects.filter(
            imovel=imovel,
            status__in=[Reserva.Status.PENDENTE, Reserva.Status.APROVADA],
            data_inicio__lt=fim,
            data_fim__gt=inicio,
        ).exists()
        if conflito:
            raise serializers.ValidationError('Este imóvel já possui reserva para o período selecionado.')

        return dados

    def create(self, validated_data):
        imovel = validated_data['imovel']
        dias = (validated_data['data_fim'] - validated_data['data_inicio']).days
        validated_data['valor_total'] = imovel.preco_diaria * dias
        validated_data['hospede'] = self.context['request'].user
        return super().create(validated_data)


class ReservaStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reserva
        fields = ['status']

    def validate_status(self, valor):
        if valor not in (Reserva.Status.APROVADA, Reserva.Status.RECUSADA):
            raise serializers.ValidationError('Status deve ser "aprovada" ou "recusada".')
        return valor
