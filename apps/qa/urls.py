from django.urls import path
from . import views

urlpatterns = [
    path("proyectos/<int:pk>/preguntas", views.preguntas_list_create, name="preguntas-list"),
    path("preguntas/<int:pk>", views.pregunta_detail, name="pregunta-detail"),
    path("preguntas/<int:pk>/respuestas", views.crear_respuesta, name="respuesta-create"),
    path("preguntas/<int:pk>/resolver", views.resolver_pregunta, name="pregunta-resolver"),
]
