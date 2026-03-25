"""
Helpers de permisos para proyectos.
Centraliza la lógica de "¿puede este usuario hacer X en este proyecto?".
"""
from .models import ColaboradorProyecto
from apps.authentication.models import User


def get_rol_en_proyecto(user: User, proyecto) -> str | None:
    """Devuelve el rol del usuario en el proyecto, o None si no tiene acceso."""
    if user.rol == User.ROL_ADMIN:
        return ColaboradorProyecto.ROL_OWNER  # Admin tiene acceso total
    try:
        col = ColaboradorProyecto.objects.get(proyecto=proyecto, usuario=user)
        return col.rol_en_proyecto
    except ColaboradorProyecto.DoesNotExist:
        return None


def puede_editar(user: User, proyecto) -> bool:
    rol = get_rol_en_proyecto(user, proyecto)
    return rol in (ColaboradorProyecto.ROL_OWNER, ColaboradorProyecto.ROL_EDITOR)


def puede_ver(user: User, proyecto) -> bool:
    rol = get_rol_en_proyecto(user, proyecto)
    return rol is not None


def puede_administrar(user: User, proyecto) -> bool:
    if user.rol == User.ROL_ADMIN:
        return True
    rol = get_rol_en_proyecto(user, proyecto)
    return rol == ColaboradorProyecto.ROL_OWNER
