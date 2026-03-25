from django.urls import path
from . import views

urlpatterns = [
    path("proyectos/<int:pk>/notas-importantes", views.notas_list_create, name="notas-list"),
    path("notas-importantes/<int:pk>", views.nota_detail, name="nota-detail"),
]
