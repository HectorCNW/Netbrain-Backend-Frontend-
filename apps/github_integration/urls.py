from django.urls import path
from . import views

urlpatterns = [
    path("proyectos/<int:pk>/github/conectar", views.conectar_github, name="github-conectar"),
    path("proyectos/<int:pk>/github/prs", views.listar_prs, name="github-prs"),
    path("proyectos/<int:pk>/github/sync", views.sync_github, name="github-sync"),
    path("proyectos/<int:pk>/github/resumen", views.resumen_github, name="github-resumen"),
]
