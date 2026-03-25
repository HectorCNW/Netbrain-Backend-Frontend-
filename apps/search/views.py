from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from apps.projects.models import ProyectoWiki, ColaboradorProyecto
from apps.pages.models import PaginaWiki
from apps.qa.models import PreguntaProyecto
from apps.important_notes.models import NotaImportanteProyecto
from apps.pages.serializers import PaginaWikiListSerializer
from apps.projects.serializers import ProyectoWikiSerializer
from apps.qa.serializers import PreguntaListSerializer
from apps.important_notes.serializers import NotaImportanteSerializer
from apps.authentication.models import User


def _proyectos_visibles(user):
    """IDs de proyectos que el usuario puede ver."""
    if user.rol == User.ROL_ADMIN:
        return ProyectoWiki.objects.values_list("id", flat=True)
    return ColaboradorProyecto.objects.filter(usuario=user).values_list("proyecto_id", flat=True)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def buscar(request):
    """
    Búsqueda global con filtros.

    Query params:
      q            — texto libre (obligatorio)
      proyectoId   — limitar a un proyecto
      lenguaje     — filtrar proyectos por lenguaje
      autor        — ID de usuario autor/editor
      tag          — tag de página o pregunta
      fechaDesde   — ISO date
      fechaHasta   — ISO date
      tipo         — "proyecto" | "pagina" | "pregunta" | "nota" (si no se pasa, devuelve todo)
    """
    q = request.query_params.get("q", "").strip()
    proyecto_id = request.query_params.get("proyectoId")
    lenguaje = request.query_params.get("lenguaje")
    autor_id = request.query_params.get("autor")
    tag = request.query_params.get("tag")
    fecha_desde = request.query_params.get("fechaDesde")
    fecha_hasta = request.query_params.get("fechaHasta")
    tipo = request.query_params.get("tipo", "")

    if not q:
        return Response({"error": "El parámetro 'q' es obligatorio"}, status=400)

    proyectos_ids = _proyectos_visibles(request.user)
    if proyecto_id:
        proyectos_ids = [int(proyecto_id)]

    resultados = {}

    # -- Proyectos --
    if not tipo or tipo == "proyecto":
        qs = ProyectoWiki.objects.filter(
            id__in=proyectos_ids,
        ).filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )
        if lenguaje:
            qs = qs.filter(lenguajes__contains=[lenguaje])
        resultados["proyectos"] = ProyectoWikiSerializer(qs[:10], many=True, context={"request": request}).data

    # -- Páginas --
    if not tipo or tipo == "pagina":
        qs = PaginaWiki.objects.filter(
            proyecto_id__in=proyectos_ids,
        ).filter(
            Q(titulo__icontains=q) | Q(contenido_markdown__icontains=q)
        ).select_related("creado_por", "ultima_edicion_por", "proyecto")
        if tag:
            qs = qs.filter(tags__contains=[tag])
        if autor_id:
            qs = qs.filter(Q(creado_por_id=autor_id) | Q(ultima_edicion_por_id=autor_id))
        if fecha_desde:
            qs = qs.filter(fecha_actualizacion__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_actualizacion__date__lte=fecha_hasta)
        resultados["paginas"] = PaginaWikiListSerializer(qs[:20], many=True).data

    # -- Preguntas --
    if not tipo or tipo == "pregunta":
        qs = PreguntaProyecto.objects.filter(
            proyecto_id__in=proyectos_ids,
        ).filter(
            Q(titulo__icontains=q) | Q(pregunta__icontains=q)
        ).select_related("creado_por")
        if tag:
            qs = qs.filter(tags__contains=[tag])
        if autor_id:
            qs = qs.filter(creado_por_id=autor_id)
        resultados["preguntas"] = PreguntaListSerializer(qs[:10], many=True).data

    # -- Notas importantes --
    if not tipo or tipo == "nota":
        qs = NotaImportanteProyecto.objects.filter(
            proyecto_id__in=proyectos_ids,
        ).filter(
            Q(titulo__icontains=q) | Q(contenido_markdown__icontains=q)
        ).select_related("creado_por")
        resultados["notas"] = NotaImportanteSerializer(qs[:10], many=True).data

    return Response(resultados)
