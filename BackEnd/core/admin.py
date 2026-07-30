from django.contrib import admin

from .models import Avaliacao, Comodidade, ImagemImovel, Imovel, Reserva


class ImagemImovelInline(admin.TabularInline):
    """Permite adicionar/editar as imagens direto na tela do Imóvel."""
    model = ImagemImovel
    extra = 1


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cidade', 'anfitriao', 'preco_diaria', 'capacidade_maxima', 'data_criacao')
    list_filter = ('cidade',)
    search_fields = ('titulo', 'cidade', 'anfitriao__username')
    inlines = [ImagemImovelInline]


@admin.register(Comodidade)
class ComodidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'icone')
    search_fields = ('nome',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'imovel', 'hospede', 'data_inicio', 'data_fim', 'status', 'valor_total')
    list_filter = ('status',)
    search_fields = ('imovel__titulo', 'hospede__username')


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'usuario', 'nota', 'data_criacao')
    list_filter = ('nota',)
