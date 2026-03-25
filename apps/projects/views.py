from django.shortcuts import get_object_or_404
from rest_framework import status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import ProyectoWiki, ColaboradorProyecto, ActividadProyecto
from .serializers import ProyectoWikiSerializer, ColaboradorSerializer, ActividadProyectoSerializer
from .permissions import puede_ver, puede_editar, puede_administrar
from apps.authentication.models import User


def registrar_actividad(proyecto, usuario, tipo_evento, entidad="", entidad_id=None, metadata=None):
    ActividadProyecto.objects.create(
        proyecto=proyecto,
        usuario=usuario,
        tipo_evento=tipo_evento,
        entidad=entidad,
        entidad_id=entidad_id,
        metadata=metadata or {},
    )


# ---------------------------------------------------------------------------
# Proyectos CRUD
# ---------------------------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def proyectos_list_create(request):
    if request.method == "GET":
        if request.user.rol == User.ROL_ADMIN:
            qs = ProyectoWiki.objects.all()
        else:
            colaboraciones = ColaboradorProyecto.objects.filter(usuario=request.user).values_list("proyecto_id", flat=True)
            qs = ProyectoWiki.objects.filter(id__in=colaboraciones)

        # Filtros opcionales
        estado = request.query_params.get("estado")
        lenguaje = request.query_params.get("lenguaje")
        if estado:
            qs = qs.filter(estado=estado)
        if lenguaje:
            qs = qs.filter(lenguajes__contains=[lenguaje])

        serializer = ProyectoWikiSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    if request.method == "POST":
        if request.user.rol == User.ROL_VIEWER:
            return Response({"error": "Sin permisos para crear proyectos"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProyectoWikiSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        proyecto = serializer.save()
        registrar_actividad(proyecto, request.user, "proyecto_creado", "proyecto", proyecto.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def proyecto_detail(request, pk):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)

    if not puede_ver(request.user, proyecto):
        return Response({"error": "Sin acceso a este proyecto"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = ProyectoWikiSerializer(proyecto, context={"request": request})
        return Response(serializer.data)

    if request.method == "PATCH":
        if not puede_administrar(request.user, proyecto):
            return Response({"error": "Solo el owner o admin puede editar metadatos"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProyectoWikiSerializer(proyecto, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    if request.method == "DELETE":
        if not puede_administrar(request.user, proyecto):
            return Response({"error": "Sin permisos para eliminar"}, status=status.HTTP_403_FORBIDDEN)
        proyecto.estado = ProyectoWiki.ESTADO_ARCHIVADO
        proyecto.save()
        return Response({"mensaje": "Proyecto archivado"}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Colaboradores
# ---------------------------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def colaboradores_list_create(request, pk):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        cols = proyecto.colaboradores.select_related("usuario")
        return Response(ColaboradorSerializer(cols, many=True).data)

    if request.method == "POST":
        if not puede_administrar(request.user, proyecto):
            return Response({"error": "Solo owner o admin puede añadir colaboradores"}, status=status.HTTP_403_FORBIDDEN)
        data = {**request.data, "proyecto": proyecto.id}
        serializer = ColaboradorSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(proyecto=proyecto)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def colaborador_detail(request, pk, col_id):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    colaborador = get_object_or_404(ColaboradorProyecto, pk=col_id, proyecto=proyecto)

    if not puede_administrar(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "PATCH":
        serializer = ColaboradorSerializer(colaborador, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    if request.method == "DELETE":
        colaborador.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Actividad del proyecto (timeline)
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def proyecto_actividad(request, pk):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)
    actividades = proyecto.actividades.select_related("usuario")[:50]
    return Response(ActividadProyectoSerializer(actividades, many=True).data)
