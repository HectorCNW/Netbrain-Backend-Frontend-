from django.db import models
from apps.authentication.models import User


class ProyectoWiki(models.Model):
    ESTADO_ACTIVO = "activo"
    ESTADO_ARCHIVADO = "archivado"
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_ARCHIVADO, "Archivado"),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="proyectos_owned")
    lenguajes = models.JSONField(default=list)        # ["TypeScript", "Python", "SQL"]
    repositorios = models.JSONField(default=list)     # ["https://github.com/org/repo"]
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto Wiki"
        verbose_name_plural = "Proyectos Wiki"
        ordering = ["-fecha_actualizacion"]

    def __str__(self):
        return self.nombre


class ColaboradorProyecto(models.Model):
    ROL_OWNER = "owner"
    ROL_EDITOR = "editor"
    ROL_VIEWER = "viewer"
    ROL_CHOICES = [
        (ROL_OWNER, "Owner"),
        (ROL_EDITOR, "Editor"),
        (ROL_VIEWER, "Viewer"),
    ]

    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="colaboradores")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="colaboraciones")
    rol_en_proyecto = models.CharField(max_length=10, choices=ROL_CHOICES, default=ROL_VIEWER)
    fecha_alta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("proyecto", "usuario")
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"

    def __str__(self):
        return f"{self.usuario} → {self.proyecto} [{self.rol_en_proyecto}]"


class ActividadProyecto(models.Model):
    TIPO_CHOICES = [
        ("proyecto_creado", "Proyecto creado"),
        ("pagina_creada", "Página creada"),
        ("pagina_editada", "Página editada"),
        ("pagina_eliminada", "Página eliminada"),
        ("export_pdf", "Exportación PDF"),
        ("github_sync", "Sync GitHub"),
        ("nota_creada", "Nota importante creada"),
        ("pregunta_creada", "Pregunta creada"),
        ("respuesta_creada", "Respuesta creada"),
        ("documento_subido", "Documento subido"),
    ]

    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="actividades")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="actividades")
    tipo_evento = models.CharField(max_length=30, choices=TIPO_CHOICES)
    entidad = models.CharField(max_length=30, blank=True)   # "proyecto" | "pagina" | ...
    entidad_id = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ["-fecha"]

    def __str__(self):
        return f"[{self.proyecto}] {self.tipo_evento} — {self.fecha:%Y-%m-%d %H:%M}"
