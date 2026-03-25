from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import PreguntaProyecto, RespuestaProyecto


class RespuestaSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)

    class Meta:
        model = RespuestaProyecto
        fields = ["id", "respuesta", "creado_por", "es_aceptada", "fecha_creacion"]
        read_only_fields = ["id", "creado_por", "fecha_creacion"]


class PreguntaSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)
    respuestas = RespuestaSerializer(many=True, read_only=True)
    total_respuestas = serializers.SerializerMethodField()

    class Meta:
        model = PreguntaProyecto
        fields = [
            "id", "proyecto", "titulo", "pregunta", "creado_por",
            "estado", "tags", "fecha_creacion", "fecha_actualizacion",
            "respuestas", "total_respuestas",
        ]
        read_only_fields = ["id", "proyecto", "creado_por", "fecha_creacion", "fecha_actualizacion", "estado"]

    def get_total_respuestas(self, obj):
        return obj.respuestas.count()


class PreguntaListSerializer(serializers.ModelSerializer):
    creado_por = UserSerializer(read_only=True)
    total_respuestas = serializers.SerializerMethodField()

    class Meta:
        model = PreguntaProyecto
        fields = ["id", "titulo", "estado", "tags", "creado_por", "fecha_creacion", "total_respuestas"]

    def get_total_respuestas(self, obj):
        return obj.respuestas.count()
