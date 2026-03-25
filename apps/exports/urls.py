from django.urls import path
from . import views

urlpatterns = [
    path("paginas/<int:pk>/exportar.pdf", views.exportar_pagina, name="exportar-pagina-pdf"),
    path("proyectos/<int:pk>/exportar.pdf", views.exportar_proyecto, name="exportar-proyecto-pdf"),
]
