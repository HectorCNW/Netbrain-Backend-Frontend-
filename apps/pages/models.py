from django.db import models
from django.utils.text import slugify
from apps.authentication.models import User
from apps.projects.models import ProyectoWiki


class PaginaWiki(models.Model):
    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="paginas")
    titulo = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320)
    contenido_markdown = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="paginas_creadas")
    ultima_edicion_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="paginas_editadas")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    version_actual = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("proyecto", "slug")
        verbose_name = "Página Wiki"
        verbose_name_plural = "Páginas Wiki"
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.proyecto.nombre} / {self.titulo}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)


class VersionPaginaWiki(models.Model):
    pagina = models.ForeignKey(PaginaWiki, on_delete=models.CASCADE, related_name="versiones")
    numero_version = models.PositiveIntegerField()
    contenido_markdown = models.TextField()
    editado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="versiones_editadas")
    mensaje_cambio = models.CharField(max_length=500, blank=True)
    fecha_edicion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("pagina", "numero_version")
        verbose_name = "Versión de Página"
        verbose_name_plural = "Versiones de Página"
        ordering = ["-numero_version"]

    def __str__(self):
        return f"{self.pagina.titulo} v{self.numero_version}"
