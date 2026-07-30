from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class RegistroSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password',
            'telefone', 'endereco', 'cidade', 'cep',
        ]

    def create(self, validated_data):
        senha = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(senha)
        usuario.save()
        return usuario


class UsuarioSerializer(serializers.ModelSerializer):

    eh_anfitriao = serializers.BooleanField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email',
            'telefone', 'endereco', 'cidade', 'cep',
            'eh_anfitriao', 'data_criacao',
        ]
        read_only_fields = ['id', 'username', 'data_criacao']
