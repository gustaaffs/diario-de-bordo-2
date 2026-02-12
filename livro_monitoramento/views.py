from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Count, Q, Prefetch

from .models import Registro, LogAcao, LinkImportante, CategoriaApoio
from .forms import RegistroForm
from .filters import RegistroFilter, LogAcaoFilter


def _diff_registro(old_obj, new_obj):
    """
    Retorna dict no formato:
    {"campo": {"old": "...", "new": "..."}, ...}
    incluindo tipo com nome antigo -> nome novo
    """
    changes = {}

    # campos texto
    for field in ["titulo", "texto"]:
        old_v = getattr(old_obj, field, "") or ""
        new_v = getattr(new_obj, field, "") or ""
        if old_v != new_v:
            changes[field] = {"old": old_v, "new": new_v}

    # tipo (FK) - salva NOME antigo -> NOME novo
    old_tipo_id = getattr(old_obj, "tipo_id", None)
    new_tipo_id = getattr(new_obj, "tipo_id", None)
    if old_tipo_id != new_tipo_id:
        old_nome = getattr(getattr(old_obj, "tipo", None), "nome", "") if old_tipo_id else ""
        new_nome = getattr(getattr(new_obj, "tipo", None), "nome", "") if new_tipo_id else ""
        changes["tipo"] = {"old": old_nome, "new": new_nome}

    return changes


def livro_home(request):
    qs = Registro.objects.select_related("tipo", "autor").all()

    f = RegistroFilter(request.GET, queryset=qs)
    registros = f.qs

    form = RegistroForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Você precisa estar logado para adicionar registros.")

        form = RegistroForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.autor = request.user
            obj.save()

            # LOG CREATE (usuário real)
            LogAcao.objects.create(
                usuario=request.user,
                acao="CREATE",
                tipo=obj.tipo,
                registro_id=obj.id,
                titulo=obj.titulo or "",
                detalhes={}
            )

            messages.success(request, "Registro criado com sucesso.")
            return redirect("livro:home")

    context = {
        "filter": f,
        "registros": registros,
        "form": form,
    }
    return render(request, "livro_monitoramento/livro_home.html", context)


@login_required
def editar_registro(request, pk):
    registro = get_object_or_404(Registro, pk=pk)

    if not (request.user.is_staff or registro.autor_id == request.user.id):
        return HttpResponseForbidden("Sem permissão para editar.")

    if request.method == "POST":
        old = Registro.objects.select_related("tipo").get(pk=registro.pk)

        form = RegistroForm(request.POST, instance=registro)
        if form.is_valid():
            updated = form.save()

            changes = _diff_registro(old, updated)

            if changes:
                LogAcao.objects.create(
                    usuario=request.user,
                    acao="UPDATE",
                    tipo=updated.tipo,
                    registro_id=updated.id,
                    titulo=updated.titulo or "",
                    detalhes=changes
                )

            messages.success(request, "Registro atualizado.")
            return redirect("livro:home")
    else:
        form = RegistroForm(instance=registro)

    return render(request, "livro_monitoramento/editar_registro.html", {
        "form": form,
        "registro": registro
    })


@login_required
def excluir_registro(request, pk):
    registro = get_object_or_404(Registro, pk=pk)

    if not (request.user.is_staff or registro.autor_id == request.user.id):
        return HttpResponseForbidden("Sem permissão para excluir.")

    if request.method == "POST":
        # LOG DELETE antes de apagar
        LogAcao.objects.create(
            usuario=request.user,
            acao="DELETE",
            tipo=registro.tipo,
            registro_id=registro.id,
            titulo=registro.titulo or "",
            detalhes={}
        )

        registro.delete()
        messages.success(request, "Registro excluído.")
        return redirect("livro:home")

    return render(request, "livro_monitoramento/confirmar_exclusao.html", {"registro": registro})


def logs_home(request):
    qs = LogAcao.objects.select_related("usuario", "tipo").all()
    f = LogAcaoFilter(request.GET, queryset=qs)
    logs = f.qs

    return render(request, "livro_monitoramento/logs_home.html", {
        "filter": f,
        "logs": logs,
    })

def links_home(request):
    itens_ativos = LinkImportante.objects.filter(ativo=True).order_by("ordem", "titulo")

    categorias = (
        CategoriaApoio.objects
        .filter(ativo=True)
        .annotate(qtd=Count("itens", filter=Q(itens__ativo=True)))
        .filter(qtd__gt=0)
        .prefetch_related(Prefetch("itens", queryset=itens_ativos))
        .order_by("ordem", "nome")
    )

    sem_categoria = itens_ativos.filter(categoria__isnull=True)

    return render(request, "livro_monitoramento/links_home.html", {
        "categorias": categorias,
        "sem_categoria": sem_categoria,
    })