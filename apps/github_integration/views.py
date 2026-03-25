from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import ProyectoWiki
from apps.projects.permissions import puede_ver, puede_administrar
from apps.projects.views import registrar_actividad
from .models import IntegracionGitHub, PullRequestSnapshot
from .serializers import IntegracionGitHubSerializer, PullRequestSerializer
from . import services


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def conectar_github(request, pk):
    """Conecta un proyecto a un repositorio GitHub."""
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_administrar(request.user, proyecto):
        return Response({"error": "Solo owner o admin puede conectar GitHub"}, status=status.HTTP_403_FORBIDDEN)

    owner_repo = request.data.get("owner_repo", "").strip()
    if not owner_repo or "/" not in owner_repo:
        return Response({"error": "Formato requerido: org/repositorio"}, status=status.HTTP_400_BAD_REQUEST)

    verificacion = services.verificar_repo(owner_repo)
    if not verificacion.get("ok"):
        return Response({"error": verificacion.get("error", "Repositorio no accesible")}, status=status.HTTP_400_BAD_REQUEST)

    integracion, _ = IntegracionGitHub.objects.update_or_create(
        proyecto=proyecto,
        defaults={
            "owner_repo": owner_repo,
            "repo_url": f"https://github.com/{owner_repo}",
            "sync_activa": True,
        },
    )
    return Response(IntegracionGitHubSerializer(integracion).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_prs(request, pk):
    """Lista los PRs guardados del proyecto, con filtros opcionales."""
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    qs = PullRequestSnapshot.objects.filter(proyecto=proyecto)

    estado = request.query_params.get("estado")
    autor = request.query_params.get("autor")
    label = request.query_params.get("label")

    if estado:
        qs = qs.filter(estado=estado)
    if autor:
        qs = qs.filter(autor__icontains=autor)
    if label:
        qs = qs.filter(labels__contains=[label])

    return Response(PullRequestSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_github(request, pk):
    """Dispara sincronización manual de PRs desde GitHub."""
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_administrar(request.user, proyecto):
        return Response({"error": "Sin permisos para sincronizar"}, status=status.HTTP_403_FORBIDDEN)

    integracion = getattr(proyecto, "integracion_github", None)
    if not integracion:
        return Response({"error": "El proyecto no tiene GitHub conectado"}, status=status.HTTP_400_BAD_REQUEST)

    resultado = services.sincronizar_prs(integracion)
    registrar_actividad(proyecto, request.user, "github_sync", "proyecto", proyecto.id, resultado)
    return Response(resultado)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_github(request, pk):
    """Devuelve datos generales del repositorio GitHub del proyecto."""
    proyecto = get_object_or_404(ProyectoWiki, pk=pk)
    if not puede_ver(request.user, proyecto):
        return Response(status=status.HTTP_403_FORBIDDEN)

    integracion = getattr(proyecto, "integracion_github", None)
    if not integracion:
        return Response({"error": "Sin integración GitHub"}, status=status.HTTP_404_NOT_FOUND)

    resumen = services.resumen_repo(integracion.owner_repo)
    # Añadimos stats locales de PRs
    prs = PullRequestSnapshot.objects.filter(proyecto=proyecto)
    resumen["prs"] = {
        "abiertas": prs.filter(estado="open").count(),
        "merged": prs.filter(estado="merged").count(),
        "cerradas": prs.filter(estado="closed").count(),
        "total": prs.count(),
        "ultima_sync": integracion.ultima_sync,
    }
    return Response(resumen)
