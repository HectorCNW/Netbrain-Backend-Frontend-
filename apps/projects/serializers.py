from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import ProyectoWiki, ColaboradorProyecto, ActividadProyecto


class ColaboradorSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        source="usuario",
        queryset=__import__("apps.authentication.models", fromlist=["User"]).User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ColaboradorProyecto
        fields = ["id", "usuario", "usuario_id", "rol_en_proyecto", "fecha_alta"]
        read_only_fields = ["id", "fecha_alta"]


class ProyectoWikiSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        source="owner",
        queryset=__import__("apps.authentication.models", fromlist=["User"]).User.objects.all(),
        write_only=True,
        required=False,
    )
    colaboradores = ColaboradorSerializer(many=True, read_only=True)
    total_paginas = serializers.SerializerMethodField()

    class Meta:
        model = ProyectoWiki
        fields = [
            "id", "nombre", "descripcion", "owner", "owner_id",
            "lenguajes", "repositorios", "estado",
            "fecha_creacion", "fecha_actualizacion",
            "colaboradores", "total_paginas",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

    def get_total_paginas(self, obj):
        return obj.paginas.count()

    def create(self, validated_data):
        request = self.context.get("request")
        if "owner" not in validated_data and request:
            validated_data["owner"] = request.user
        proyecto = super().create(validated_data)
        # El owner también es colaborador con rol owner
        ColaboradorProyecto.objects.get_or_create(
            proyecto=proyecto,
            usuario=proyecto.owner,
            defaults={"rol_en_proyecto": ColaboradorProyecto.ROL_OWNER},
        )
        return proyecto


class ActividadProyectoSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = ActividadProyecto
        fields = ["id", "tipo_evento", "entidad", "entidad_id", "metadata", "fecha", "usuario"]
