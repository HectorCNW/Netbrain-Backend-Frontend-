from django.urls import path
from . import views

urlpatterns = [
    path("proyectos", views.proyectos_list_create, name="proyectos-list"),
    path("proyectos/<int:pk>", views.proyecto_detail, name="proyecto-detail"),
    path("proyectos/<int:pk>/colaboradores", views.colaboradores_list_create, name="colaboradores-list"),
    path("proyectos/<int:pk>/colaboradores/<int:col_id>", views.colaborador_detail, name="colaborador-detail"),
    path("proyectos/<int:pk>/actividad", views.proyecto_actividad, name="proyecto-actividad"),
]
