from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import ProyectoWiki
from apps.projects.permissions import puede_ver, puede_editar
from apps.projects.views import registrar_actividad
from .models import NotaImportanteProyecto
from .serializers import NotaImportanteSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def notas_list_create(request, pk):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        qs = proyecto.notas_importantes.select_related("creado_por")
        tipo = request.query_params.get("tipo")
        prioridad = request.query_params.get("prioridad")
        if tipo:
            qs = qs.filter(tipo=tipo)
        if prioridad:
            qs = qs.filter(prioridad=prioridad)
        return Response(NotaImportanteSerializer(qs, many=True).data)

    if request.method == "POST":
        if not puede_editar(request.user, proyecto):
            return Response({"error": "Sin permisos para crear notas"}, status=status.HTTP_403_FORBIDDEN)
        serializer = NotaImportanteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nota = serializer.save(proyecto=proyecto, creado_por=request.user)
        registrar_actividad(
            proyecto, request.user, "nota_creada", "nota", nota.id,
            {"titulo": nota.titulo, "tipo": nota.tipo, "prioridad": nota.prioridad},
        )
        return Response(NotaImportanteSerializer(nota).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def nota_detail(request, pk):
    nota = get_object_or_404(NotaImportanteProyecto.objects.select_related("proyecto", "creado_por"), pk=pk)
    if not puede_ver(request.user, nota.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(NotaImportanteSerializer(nota).data)

    if request.method == "PATCH":
        if not puede_editar(request.user, nota.proyecto):
            return Response({"error": "Sin permisos para editar"}, status=status.HTTP_403_FORBIDDEN)
        serializer = NotaImportanteSerializer(nota, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NotaImportanteSerializer(nota).data)

    if request.method == "DELETE":
        if not puede_editar(request.user, nota.proyecto):
            return Response(status=status.HTTP_403_FORBIDDEN)
        nota.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
