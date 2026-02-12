from django.urls import path
from . import views

app_name = "livro"

urlpatterns = [
    path("", views.livro_home, name="home"),

    # editar/excluir (nomes batendo com views.py)
    path("editar/<int:pk>/", views.editar_registro, name="editar"),
    path("excluir/<int:pk>/", views.excluir_registro, name="excluir"),
    path("logs/", views.logs_home, name="logs"),
    path("links/", views.links_home, name="links"),
]
