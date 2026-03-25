from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import ProyectoWiki
from apps.projects.permissions import puede_ver, puede_editar
from apps.projects.views import registrar_actividad
from .models import PreguntaProyecto, RespuestaProyecto
from .serializers import PreguntaSerializer, PreguntaListSerializer, RespuestaSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def preguntas_list_create(request, pk):
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        qs = proyecto.preguntas.select_related("creado_por")
        q = request.query_params.get("q")
        estado = request.query_params.get("estado")
        tag = request.query_params.get("tag")
        if q:
            qs = qs.filter(titulo__icontains=q) | qs.filter(pregunta__icontains=q)
        if estado:
            qs = qs.filter(estado=estado)
        if tag:
            qs = qs.filter(tags__contains=[tag])
        return Response(PreguntaListSerializer(qs, many=True).data)

    if request.method == "POST":
        serializer = PreguntaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pregunta = serializer.save(proyecto=proyecto, creado_por=request.user)
        registrar_actividad(proyecto, request.user, "pregunta_creada", "pregunta", pregunta.id, {"titulo": pregunta.titulo})
        return Response(PreguntaSerializer(pregunta).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pregunta_detail(request, pk):
    pregunta = get_object_or_404(PreguntaProyecto.objects.prefetch_related("respuestas__creado_por"), pk=pk)
    if not puede_ver(request.user, pregunta.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)
    return Response(PreguntaSerializer(pregunta).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_respuesta(request, pk):
    pregunta = get_object_or_404(PreguntaProyecto, pk=pk)
    if not puede_ver(request.user, pregunta.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)
    serializer = RespuestaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    respuesta = serializer.save(pregunta=pregunta, creado_por=request.user)
    registrar_actividad(
        pregunta.proyecto, request.user, "respuesta_creada", "pregunta", pregunta.id,
        {"pregunta": pregunta.titulo},
    )
    return Response(RespuestaSerializer(respuesta).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def resolver_pregunta(request, pk):
    pregunta = get_object_or_404(PreguntaProyecto, pk=pk)
    if not puede_editar(request.user, pregunta.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    # Aceptar respuesta si se pasa respuesta_id
    respuesta_id = request.data.get("respuesta_id")
    if respuesta_id:
        RespuestaProyecto.objects.filter(pregunta=pregunta).update(es_aceptada=False)
        RespuestaProyecto.objects.filter(pk=respuesta_id, pregunta=pregunta).update(es_aceptada=True)

    pregunta.estado = PreguntaProyecto.ESTADO_RESUELTA
    pregunta.save(update_fields=["estado"])
    return Response(PreguntaSerializer(pregunta).data)
