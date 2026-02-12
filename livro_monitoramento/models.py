from django.db import models
from django.conf import settings


class TipoRegistro(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Tipo de Registro"
        verbose_name_plural = "Tipos de Registro"

    def __str__(self):
        return self.nome


class Registro(models.Model):
    tipo = models.ForeignKey(TipoRegistro, on_delete=models.PROTECT, related_name="registros")
    titulo = models.CharField(max_length=200)
    texto = models.TextField()

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registros_livro",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"

class LogAcao(models.Model):
    ACAO_CHOICES = [
        ("CREATE", "Criou"),
        ("UPDATE", "Atualizou"),
        ("DELETE", "Excluiu"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="logs_livro",
    )

    acao = models.CharField(max_length=10, choices=ACAO_CHOICES)
    tipo = models.ForeignKey(
        "TipoRegistro",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="logs",
    )

    registro_id = models.IntegerField(null=True, blank=True)

    titulo = models.CharField(max_length=255, blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    # detalhes do que mudou: {"campo": {"old": "...", "new": "..."}, ...}
    detalhes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_acao_display()} • {self.titulo} • {self.criado_em:%d/%m/%Y %H:%M}"

class CategoriaApoio(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Categoria de Apoio"
        verbose_name_plural = "Categorias de Apoio"

    def __str__(self):
        return self.nome


class LinkImportante(models.Model):
    categoria = models.ForeignKey(
        CategoriaApoio,
        on_delete=models.PROTECT,
        related_name="itens",
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=140)
    descricao = models.CharField(max_length=255, blank=True, default="")
    url = models.URLField(blank=True, default="")
    conteudo = models.TextField(blank=True, default="")
    icone = models.CharField(max_length=8, blank=True, default="📌")
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "titulo"]
        verbose_name = "Item de Apoio"
        verbose_name_plural = "Itens de Apoio"

    def __str__(self):
        return self.titulo