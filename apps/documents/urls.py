from django.urls import path
from . import views

urlpatterns = [
    path("proyectos/<int:pk>/documentos", views.documentos_list_create, name="documentos-list"),
    path("documentos/<int:pk>", views.documento_detail, name="documento-detail"),
]
