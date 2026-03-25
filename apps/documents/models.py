import os
from django.db import models
from apps.authentication.models import User
from apps.projects.models import ProyectoWiki


def documento_upload_path(instance, filename):
    """Sube archivos a media/proyectos/<proyecto_id>/documentos/<filename>"""
    return os.path.join("proyectos", str(instance.proyecto_id), "documentos", filename)


class DocumentoProyecto(models.Model):
    TIPO_PDF = "pdf"
    TIPO_MARKDOWN = "markdown"
    TIPO_CHOICES = [
        (TIPO_PDF, "PDF"),
        (TIPO_MARKDOWN, "Markdown"),
    ]

    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="documentos")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=300)
    archivo = models.FileField(upload_to=documento_upload_path)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="documentos_subidos")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_subida"]
        verbose_name = "Documento"

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    @property
    def url_archivo(self):
        if self.archivo:
            return self.archivo.url
        return ""
