from django.urls import path
from . import views
from .api_views import RegistroCreateAPIView, RegistroUpdateAPIView

app_name = "livro"

urlpatterns = [
    path("", views.livro_home, name="home"),

    path("editar/<int:pk>/", views.editar_registro, name="editar"),
    path("excluir/<int:pk>/", views.excluir_registro, name="excluir"),
    path("logs/", views.logs_home, name="logs"),
    path("links/", views.links_home, name="links"),
    path("exportar-excel/", views.exportar_excel, name="exportar_excel"),

    path("api/registros/", RegistroCreateAPIView.as_view(), name="api_registro_create"),
    path("api/registros/<int:pk>/", RegistroUpdateAPIView.as_view(), name="api_registro_update"),
]
