from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'cidade', 'is_staff', 'data_criacao')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações adicionais', {
            'fields': ('telefone', 'endereco', 'cidade', 'cep'),
        }),
    )
