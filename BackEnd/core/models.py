from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models



class Comodidade(models.Model):
    """Uma comodidade que um imóvel pode ter (Wi-Fi, piscina, ar-condicionado...)."""

    nome = models.CharField(max_length=100, unique=True)
    icone = models.CharField(
        max_length=50, blank=True,
        help_text='Nome/identificador do ícone a ser usado no front-end (opcional).'
    )

    class Meta:
        verbose_name = 'Comodidade'
        verbose_name_plural = 'Comodidades'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
class Imovel(models.Model):
    """Um imóvel disponível para aluguel, cadastrado por um anfitrião."""

    anfitriao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='imoveis',
    )
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()

    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    capacidade_maxima = models.PositiveIntegerField()
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)

    comodidades = models.ManyToManyField(Comodidade, related_name='imoveis', blank=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imóvel'
        verbose_name_plural = 'Imóveis'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.titulo} ({self.cidade})'

    @property
    def nota_media(self):
        """Média das avaliações recebidas por este imóvel"""
        agregada = self.avaliacoes.aggregate(media=models.Avg('nota'))['media']
        return round(agregada, 1) if agregada is not None else None

class ImagemImovel(models.Model):
    """Uma foto pertencente à galeria de um imóvel."""

    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='imoveis/')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagem do Imóvel'
        verbose_name_plural = 'Imagens do Imóvel'
        ordering = ['ordem']

    def __str__(self):
        return f'Imagem #{self.ordem} de {self.imovel.titulo}'

class Reserva(models.Model):
    """Uma solicitação de reserva feita por um hóspede"""

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        APROVADA = 'aprovada', 'Aprovada'
        RECUSADA = 'recusada', 'Recusada'

    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='reservas')
    hospede = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservas',
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Reserva #{self.id} - {self.imovel.titulo} ({self.status})'

    def clean(self):
        if self.data_fim <= self.data_inicio:
            raise ValidationError('A data de término deve ser posterior à data de início.')


class Avaliacao(models.Model):
    """Avaliação de um imóvel feita por um hóspede"""

    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avaliacoes',
    )
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='avaliacao')
    nota = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    descricao_avaliacao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Avaliação #{self.id} - {self.imovel.titulo} ({self.nota}★)'

    def clean(self):
        if self.reserva.imovel_id != self.imovel_id:
            raise ValidationError('A reserva informada não pertence a este imóvel.')
        if self.reserva.hospede_id != self.usuario_id:
            raise ValidationError('Você só pode avaliar usando uma reserva feita por você.')
        if self.reserva.status != Reserva.Status.APROVADA:
            raise ValidationError('Só é possível avaliar imóveis de reservas aprovadas/concluídas.')
