from django.contrib import admin
from .models import DocumentoProyecto

@admin.register(DocumentoProyecto)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "tipo", "proyecto", "subido_por", "fecha_subida"]
    list_filter = ["tipo"]
