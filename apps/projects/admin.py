from django.contrib import admin
from .models import ProyectoWiki, ColaboradorProyecto, ActividadProyecto

@admin.register(ProyectoWiki)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "owner", "estado", "fecha_creacion"]
    list_filter = ["estado"]
    search_fields = ["nombre", "descripcion"]

@admin.register(ColaboradorProyecto)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ["proyecto", "usuario", "rol_en_proyecto", "fecha_alta"]

@admin.register(ActividadProyecto)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ["proyecto", "usuario", "tipo_evento", "fecha"]
    list_filter = ["tipo_evento"]
