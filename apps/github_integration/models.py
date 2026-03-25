from django.db import models
from apps.projects.models import ProyectoWiki


class IntegracionGitHub(models.Model):
    proyecto = models.OneToOneField(ProyectoWiki, on_delete=models.CASCADE, related_name="integracion_github")
    provider = models.CharField(max_length=20, default="github")
    owner_repo = models.CharField(max_length=200)   # "org/repositorio"
    repo_url = models.URLField()
    sync_activa = models.BooleanField(default=True)
    ultima_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Integración GitHub"

    def __str__(self):
        return f"{self.proyecto} → {self.owner_repo}"


class PullRequestSnapshot(models.Model):
    ESTADO_OPEN = "open"
    ESTADO_MERGED = "merged"
    ESTADO_CLOSED = "closed"
    ESTADO_CHOICES = [
        (ESTADO_OPEN, "Abierta"),
        (ESTADO_MERGED, "Merged"),
        (ESTADO_CLOSED, "Cerrada"),
    ]

    proyecto = models.ForeignKey(ProyectoWiki, on_delete=models.CASCADE, related_name="pull_requests")
    pr_number = models.PositiveIntegerField()
    titulo = models.CharField(max_length=500)
    autor = models.CharField(max_length=150)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    rama_origen = models.CharField(max_length=200)
    rama_destino = models.CharField(max_length=200)
    labels = models.JSONField(default=list)
    url = models.URLField(blank=True)
    updated_at = models.DateTimeField()

    class Meta:
        unique_together = ("proyecto", "pr_number")
        ordering = ["-updated_at"]
        verbose_name = "Pull Request"

    def __str__(self):
        return f"PR #{self.pr_number} — {self.titulo}"
