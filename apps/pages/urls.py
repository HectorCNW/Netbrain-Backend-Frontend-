from django.urls import path
from . import views

urlpatterns = [
    path("proyectos/<int:proyecto_id>/paginas", views.paginas_list_create, name="paginas-list"),
    path("paginas/<int:pk>", views.pagina_detail, name="pagina-detail"),
    path("paginas/<int:pk>/versiones", views.pagina_versiones, name="pagina-versiones"),
    path("paginas/<int:pk>/versiones/<int:numero_version>", views.pagina_version_detail, name="pagina-version-detail"),
    path("paginas/<int:pk>/restaurar/<int:numero_version>", views.pagina_restaurar_version, name="pagina-restaurar"),
]
