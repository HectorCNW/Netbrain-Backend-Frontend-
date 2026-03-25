from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os

from apps.projects.models import ProyectoWiki
from apps.projects.permissions import puede_ver, puede_editar
from apps.projects.views import registrar_actividad
from .models import DocumentoProyecto
from .serializers import DocumentoSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def documentos_list_create(request, pk):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        qs = proyecto.documentos.select_related("subido_por")
        tipo = request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo)
        return Response(DocumentoSerializer(qs, many=True, context={"request": request}).data)

    if request.method == "POST":
        if not puede_editar(request.user, proyecto):
            return Response({"error": "Sin permisos para subir documentos"}, status=status.HTTP_403_FORBIDDEN)

        serializer = DocumentoSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # Inferir tipo si no viene
        archivo = request.data.get("archivo")
        tipo = request.data.get("tipo")
        if not tipo and archivo:
            tipo = "pdf" if str(archivo).lower().endswith(".pdf") else "markdown"

        doc = serializer.save(proyecto=proyecto, subido_por=request.user, tipo=tipo or "pdf")
        registrar_actividad(
            proyecto, request.user, "documento_subido", "documento", doc.id,
            {"nombre": doc.nombre, "tipo": doc.tipo},
        )
        return Response(DocumentoSerializer(doc, context={"request": request}).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def documento_detail(request, pk):
    doc = get_object_or_404(DocumentoProyecto.objects.select_related("proyecto", "subido_por"), pk=pk)
    if not puede_ver(request.user, doc.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(DocumentoSerializer(doc, context={"request": request}).data)

    if request.method == "DELETE":
        if not puede_editar(request.user, doc.proyecto):
            return Response(status=status.HTTP_403_FORBIDDEN)
        # Eliminar archivo físico
        if doc.archivo and os.path.isfile(doc.archivo.path):
            os.remove(doc.archivo.path)
        doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
