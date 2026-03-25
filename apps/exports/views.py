from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.projects.models import ProyectoWiki
from apps.pages.models import PaginaWiki
from apps.projects.permissions import puede_ver
from apps.projects.views import registrar_actividad
from .services import exportar_pagina_pdf, exportar_proyecto_pdf


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exportar_pagina(request, pk):
    """GET /api/paginas/{id}/exportar.pdf"""
    pagina = get_object_or_404(
        PaginaWiki.objects.select_related("proyecto", "creado_por", "ultima_edicion_por"),
        pk=pk,
    )
    if not puede_ver(request.user, pagina.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    try:
        pdf_bytes = exportar_pagina_pdf(pagina)
    except RuntimeError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    nombre_archivo = f"{pagina.slug or f'pagina-{pk}'}.pdf"
    registrar_actividad(
        pagina.proyecto, request.user, "export_pdf", "pagina", pagina.id,
        {"titulo": pagina.titulo, "nombre_archivo": nombre_archivo},
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exportar_proyecto(request, pk):
    """GET /api/proyectos/{id}/exportar.pdf"""
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    try:
        pdf_bytes = exportar_proyecto_pdf(proyecto)
    except RuntimeError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    nombre_archivo = f"{proyecto.nombre.lower().replace(' ', '-')}-docs.pdf"
    registrar_actividad(
        proyecto, request.user, "export_pdf", "proyecto", proyecto.id,
        {"nombre_archivo": nombre_archivo, "total_paginas": proyecto.paginas.count()},
    )

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    return response
