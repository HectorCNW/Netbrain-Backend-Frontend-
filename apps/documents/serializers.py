from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import DocumentoProyecto


class DocumentoSerializer(serializers.ModelSerializer):
    subido_por = UserSerializer(read_only=True)
    url_archivo = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoProyecto
        fields = ["id", "proyecto", "tipo", "nombre", "archivo", "url_archivo", "subido_por", "fecha_subida"]
        read_only_fields = ["id", "proyecto", "subido_por", "fecha_subida", "url_archivo"]
        extra_kwargs = {"archivo": {"write_only": True}}

    def get_url_archivo(self, obj):
        request = self.context.get("request")
        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)
        return obj.url_archivo

    def validate_archivo(self, value):
        max_mb = 20
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"El archivo no puede superar {max_mb}MB")
        allowed = ["application/pdf", "text/markdown", "text/plain", "text/x-markdown"]
        if value.content_type not in allowed and not value.name.endswith((".pdf", ".md")):
            raise serializers.ValidationError("Solo se permiten archivos PDF o Markdown (.pdf, .md)")
        return value
