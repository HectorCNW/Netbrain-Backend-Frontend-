from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import ProyectoWiki
from apps.projects.permissions import puede_ver, puede_editar
from apps.projects.views import registrar_actividad
from .models import PaginaWiki, VersionPaginaWiki
from .serializers import PaginaWikiSerializer, PaginaWikiListSerializer, VersionPaginaSerializer


def _guardar_version(pagina, usuario, mensaje=""):
    """Crea una nueva versión snapshot de la página."""
    VersionPaginaWiki.objects.create(
        pagina=pagina,
        numero_version=pagina.version_actual,
        contenido_markdown=pagina.contenido_markdown,
        editado_por=usuario,
        mensaje_cambio=mensaje,
    )


# ---------------------------------------------------------------------------
# Páginas por proyecto
# ---------------------------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def paginas_list_create(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoWiki, pk=proyecto_id)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        qs = proyecto.paginas.select_related("creado_por", "ultima_edicion_por")
        tag = request.query_params.get("tag")
        q = request.query_params.get("q")
        if tag:
            qs = qs.filter(tags__contains=[tag])
        if q:
            qs = qs.filter(titulo__icontains=q)
        return Response(PaginaWikiListSerializer(qs, many=True).data)

    if request.method == "POST":
        if not puede_editar(request.user, proyecto):
            return Response({"error": "Sin permisos para crear páginas"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PaginaWikiSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mensaje = serializer.validated_data.pop("mensaje_cambio", "")
        pagina = serializer.save(
            proyecto=proyecto,
            creado_por=request.user,
            ultima_edicion_por=request.user,
        )
        _guardar_version(pagina, request.user, mensaje or "Página creada")
        registrar_actividad(proyecto, request.user, "pagina_creada", "pagina", pagina.id, {"titulo": pagina.titulo})
        return Response(PaginaWikiSerializer(pagina).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Página individual
# ---------------------------------------------------------------------------

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def pagina_detail(request, pk):
    pagina = get_object_or_404(PaginaWiki.objects.select_related("proyecto", "creado_por", "ultima_edicion_por"), pk=pk)
    proyecto = pagina.proyecto
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(PaginaWikiSerializer(pagina).data)

    if request.method == "PATCH":
        if not puede_editar(request.user, proyecto):
            return Response({"error": "Sin permisos para editar"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PaginaWikiSerializer(pagina, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        mensaje = serializer.validated_data.pop("mensaje_cambio", "")
        # Incrementar versión antes de guardar
        pagina.version_actual += 1
        pagina.ultima_edicion_por = request.user
        pagina = serializer.save(
            version_actual=pagina.version_actual,
            ultima_edicion_por=request.user,
        )
        _guardar_version(pagina, request.user, mensaje)
        registrar_actividad(proyecto, request.user, "pagina_editada", "pagina", pagina.id, {"titulo": pagina.titulo, "version": pagina.version_actual})
        return Response(PaginaWikiSerializer(pagina).data)

    if request.method == "DELETE":
        if not puede_editar(request.user, proyecto):
            return Response(status=status.HTTP_403_FORBIDDEN)
        titulo = pagina.titulo
        pagina.delete()
        registrar_actividad(proyecto, request.user, "pagina_eliminada", "pagina", pk, {"titulo": titulo})
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Versiones
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pagina_versiones(request, pk):
    pagina = get_object_or_404(PaginaWiki, pk=pk)
    if not puede_ver(request.user, pagina.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)
    versiones = pagina.versiones.select_related("editado_por")
    return Response(VersionPaginaSerializer(versiones, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pagina_version_detail(request, pk, numero_version):
    pagina = get_object_or_404(PaginaWiki, pk=pk)
    if not puede_ver(request.user, pagina.proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)
    version = get_object_or_404(VersionPaginaWiki, pagina=pagina, numero_version=numero_version)
    return Response(VersionPaginaSerializer(version).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pagina_restaurar_version(request, pk, numero_version):
    pagina = get_object_or_404(PaginaWiki, pk=pk)
    if not puede_editar(request.user, pagina.proyecto):
        return Response({"error": "Sin permisos para restaurar"}, status=status.HTTP_403_FORBIDDEN)
    version = get_object_or_404(VersionPaginaWiki, pagina=pagina, numero_version=numero_version)
    pagina.version_actual += 1
    pagina.contenido_markdown = version.contenido_markdown
    pagina.ultima_edicion_por = request.user
    pagina.save()
    _guardar_version(pagina, request.user, f"Restaurado desde v{numero_version}")
    registrar_actividad(
        pagina.proyecto, request.user, "pagina_editada", "pagina", pagina.id,
        {"titulo": pagina.titulo, "restaurado_desde": numero_version},
    )
    return Response(PaginaWikiSerializer(pagina).data)
