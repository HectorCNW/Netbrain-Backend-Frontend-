from django.contrib import admin
from .models import PreguntaProyecto, RespuestaProyecto

@admin.register(PreguntaProyecto)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "proyecto", "estado", "creado_por", "fecha_creacion"]
    list_filter = ["estado"]

@admin.register(RespuestaProyecto)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ["pregunta", "creado_por", "es_aceptada", "fecha_creacion"]
