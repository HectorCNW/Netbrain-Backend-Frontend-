from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import PaginaWiki, VersionPaginaWiki


class VersionPaginaSerializer(serializers.ModelSerializer):
    editado_por = UserSerializer(read_only=True)

    class Meta:
        model = VersionPaginaWiki
        fields = ["id", "numero_version", "contenido_markdown", "editado_por", "mensaje_cambio", "fecha_edicion"]
        read_only_fields = ["id", "numero_version", "fecha_edicion"]


class PaginaWikiSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)
    ultima_edicion_por = UserSerializer(read_only=True)
    mensaje_cambio = serializers.CharField(write_only=True, required=False, allow_blank=True, default="")

    class Meta:
        model = PaginaWiki
        fields = [
            "id", "proyecto", "titulo", "slug", "contenido_markdown",
            "tags", "creado_por", "ultima_edicion_por",
            "fecha_creacion", "fecha_actualizacion", "version_actual",
            "mensaje_cambio",
        ]
        read_only_fields = [
            "id", "slug", "proyecto", "creado_por", "ultima_edicion_por",
            "fecha_creacion", "fecha_actualizacion", "version_actual",
        ]


class PaginaWikiListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados."""
    creado_por = UserSerializer(read_only=True)
    ultima_edicion_por = UserSerializer(read_only=True)

    class Meta:
        model = PaginaWiki
        fields = [
            "id", "titulo", "slug", "tags",
            "creado_por", "ultima_edicion_por",
            "fecha_creacion", "fecha_actualizacion", "version_actual",
        ]
