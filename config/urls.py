from django.contrib import admin
from django.urls import path, include
from livro_monitoramento import auth_views  # vamos criar

urlpatterns = [
    path("", auth_views.login_page, name="login_page"),   # /
    path("logout/", auth_views.logout_page, name="logout_page"),
    path("livro/", include("livro_monitoramento.urls")),
    path("admin/", admin.site.urls),
]
