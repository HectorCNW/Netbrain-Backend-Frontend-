from django.db import models
from apps.authentication.models import User
from apps.projects.models import ProyectoWiki


class PreguntaProyecto(models.Model):
    ESTADO_ABIERTA = "abierta"
    ESTADO_RESUELTA = "resuelta"
    ESTADO_CHOICES = [
        (ESTADO_ABIERTA, "Abierta"),
        (ESTADO_RESUELTA, "Resuelta"),
    ]

    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="preguntas")
    titulo = models.CharField(max_length=300)
    pregunta = models.TextField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="preguntas_creadas")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default=ESTADO_ABIERTA)
    tags = models.JSONField(default=list)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Pregunta"

    def __str__(self):
        return self.titulo


class RespuestaProyecto(models.Model):
    pregunta = models.ForeignKey(PreguntaProyecto, on_delete=models.CASCADE, related_name="respuestas")
    respuesta = models.TextField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="respuestas_creadas")
    es_aceptada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-es_aceptada", "fecha_creacion"]
        verbose_name = "Respuesta"

    def __str__(self):
        return f"Respuesta a: {self.pregunta.titulo}"
