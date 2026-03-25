from django.db import models
from apps.authentication.models import User
from apps.projects.models import ProyectoWiki


class NotaImportanteProyecto(models.Model):
    TIPO_CHOICES = [
        ("funcion_clave", "Función clave"),
        ("no_tocar", "No tocar"),
        ("decision_arquitectura", "Decisión de arquitectura"),
        ("riesgo", "Riesgo conocido"),
    ]
    PRIORIDAD_CHOICES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]

    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="notas_importantes")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=300)
    contenido_markdown = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default="media")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="notas_creadas")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(prioridad="alta", then=0),
                models.When(prioridad="media", then=1),
                models.When(prioridad="baja", then=2),
                default=3,
                output_field=models.IntegerField(),
            ),
            "-fecha_actualizacion",
        ]
        verbose_name = "Nota Importante"

    def __str__(self):
        return f"[{self.tipo}] {self.titulo}"
