from django.contrib import admin
from .models import Registro, TipoRegistro, LogAcao, LinkImportante, CategoriaApoio


@admin.register(TipoRegistro)
class TipoRegistroAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    search_fields = ("nome",)
    ordering = ("ordem", "nome")


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "autor", "criado_em")
    list_filter = ("tipo", "autor", "criado_em")
    search_fields = ("titulo", "texto", "autor__username", "autor__first_name", "autor__last_name")
    ordering = ("-criado_em",)

@admin.register(LogAcao)
class LogAcaoAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "acao", "usuario", "titulo", "registro_id", "tipo")
    list_filter = ("acao", "tipo", "criado_em")
    search_fields = ("titulo", "usuario__username", "usuario__first_name", "usuario__last_name")
    readonly_fields = ("criado_em",)

@admin.register(CategoriaApoio)
class CategoriaApoioAdmin(admin.ModelAdmin):
    list_display = ("ordem", "nome", "ativo")
    list_display_links = ("nome",)
    list_editable = ("ordem", "ativo")
    search_fields = ("nome",)
    ordering = ("ordem", "nome")


@admin.register(LinkImportante)
class LinkImportanteAdmin(admin.ModelAdmin):
    list_display = ("ordem", "titulo", "categoria", "ativo", "url", "atualizado_em")
    list_display_links = ("titulo",)
    list_editable = ("ordem", "categoria", "ativo")
    search_fields = ("titulo", "descricao", "url", "conteudo")
    list_filter = ("ativo", "categoria")  # ✅ remove categoria__tipo
    ordering = ("ordem", "titulo")