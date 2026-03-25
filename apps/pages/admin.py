from django.contrib import admin
from .models import PaginaWiki, VersionPaginaWiki

@admin.register(PaginaWiki)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "proyecto", "version_actual", "ultima_edicion_por", "fecha_actualizacion"]
    search_fields = ["titulo", "contenido_markdown"]
    list_filter = ["proyecto"]

@admin.register(VersionPaginaWiki)
class VersionAdmin(admin.ModelAdmin):
    list_display = ["pagina", "numero_version", "editado_por", "fecha_edicion"]
