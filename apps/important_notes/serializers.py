from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import NotaImportanteProyecto


class NotaImportanteSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)

    class Meta:
        model = NotaImportanteProyecto
        fields = [
            "id", "proyecto", "tipo", "titulo", "contenido_markdown",
            "prioridad", "creado_por", "fecha_creacion", "fecha_actualizacion",
        ]
        read_only_fields = ["id", "proyecto", "creado_por", "fecha_creacion", "fecha_actualizacion"]
