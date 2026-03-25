from django.contrib import admin
from .models import NotaImportanteProyecto

@admin.register(NotaImportanteProyecto)
class NotaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "tipo", "prioridad", "proyecto", "creado_por"]
    list_filter = ["tipo", "prioridad"]
