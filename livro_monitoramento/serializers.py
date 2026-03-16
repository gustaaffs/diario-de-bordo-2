from rest_framework import serializers
from .models import Registro, TipoRegistro


class TipoRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRegistro
        fields = ["id", "nome"]


class RegistroSerializer(serializers.ModelSerializer):
    tipo_nome = serializers.CharField(source="tipo.nome", read_only=True)
    autor_username = serializers.CharField(source="autor.username", read_only=True)

    class Meta:
        model = Registro
        fields = ["id", "tipo", "tipo_nome", "titulo", "texto", "autor", "autor_username", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "autor", "criado_em", "atualizado_em"]
