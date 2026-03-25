"""
Servicio de integración con GitHub API.
Encapsula todas las llamadas externas para mantener las vistas limpias.
"""
import requests
from datetime import datetime, timezone
from django.conf import settings
from django.utils import timezone as dj_timezone

from .models import IntegracionGitHub, PullRequestSnapshot


GITHUB_API = settings.GITHUB_API_BASE


def _headers():
    token = settings.GITHUB_TOKEN
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def verificar_repo(owner_repo: str) -> dict:
    """Verifica que el repositorio existe y es accesible."""
    url = f"{GITHUB_API}/repos/{owner_repo}"
    resp = requests.get(url, headers=_headers(), timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        return {"ok": True, "nombre": data.get("full_name"), "privado": data.get("private", False)}
    return {"ok": False, "error": resp.json().get("message", "Repositorio no accesible")}


def sincronizar_prs(integracion: IntegracionGitHub) -> dict:
    """
    Obtiene todos los PRs (open + closed) desde GitHub y los guarda/actualiza
    en PullRequestSnapshot. Nunca expone el token en la respuesta.
    """
    owner_repo = integracion.owner_repo
    sincronizados = 0
    errores = []

    for estado in ["open", "closed"]:
        url = f"{GITHUB_API}/repos/{owner_repo}/pulls"
        params = {"state": estado, "per_page": 100}
        try:
            resp = requests.get(url, headers=_headers(), params=params, timeout=15)
            resp.raise_for_status()
            prs = resp.json()
        except requests.RequestException as e:
            errores.append(str(e))
            continue

        for pr in prs:
            merged = pr.get("merged_at") is not None
            if merged:
                estado_pr = PullRequestSnapshot.ESTADO_MERGED
            elif pr.get("state") == "closed":
                estado_pr = PullRequestSnapshot.ESTADO_CLOSED
            else:
                estado_pr = PullRequestSnapshot.ESTADO_OPEN

            updated_raw = pr.get("updated_at", "")
            try:
                updated_dt = datetime.fromisoformat(updated_raw.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                updated_dt = dj_timezone.now()

            PullRequestSnapshot.objects.update_or_create(
                proyecto=integracion.proyecto,
                pr_number=pr["number"],
                defaults={
                    "titulo": pr.get("title", ""),
                    "autor": pr.get("user", {}).get("login", ""),
                    "estado": estado_pr,
                    "rama_origen": pr.get("head", {}).get("ref", ""),
                    "rama_destino": pr.get("base", {}).get("ref", "main"),
                    "labels": [lbl["name"] for lbl in pr.get("labels", [])],
                    "url": pr.get("html_url", ""),
                    "updated_at": updated_dt,
                },
            )
            sincronizados += 1

    integracion.ultima_sync = dj_timezone.now()
    integracion.save(update_fields=["ultima_sync"])

    return {"sincronizados": sincronizados, "errores": errores}


def resumen_repo(owner_repo: str) -> dict:
    """Obtiene datos generales del repositorio (stars, forks, último commit, etc.)."""
    url = f"{GITHUB_API}/repos/{owner_repo}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "nombre": data.get("full_name"),
            "descripcion": data.get("description"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "rama_default": data.get("default_branch", "main"),
            "lenguaje_principal": data.get("language"),
            "actualizado_en": data.get("updated_at"),
            "url": data.get("html_url"),
        }
    except requests.RequestException as e:
        return {"error": str(e)}
