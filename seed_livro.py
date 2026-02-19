# /opt/livro_noc/seed_livro.py
from django.contrib.auth import get_user_model
from django.apps import apps
from django.utils import timezone


PASSWORD = "solutis@2026"

SUPERUSER_USERNAME = "gustavo.farias"

USUARIOS = [
    "lucas.clima",
    "danillo.paes",
    "gabriela.villacorta",
    "dynarte.luz",
    "welbert.santos",
    "wagner.santos",
    "felipe.msantos",
    "augusto.barbosa",
    "fabio.carvalho",
    "joao.alves",
    "david.mello",
    "thiago.ssantos",
]


def set_if_field(obj, field_name, value):
    if hasattr(obj, field_name):
        setattr(obj, field_name, value)


def get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def upsert_user(username, password, is_superuser=False):
    User = get_user_model()
    u, created = User.objects.get_or_create(username=username)

    # garante senha
    u.set_password(password)

    # flags
    if is_superuser:
        u.is_superuser = True
        u.is_staff = True
        u.is_active = True
    else:
        u.is_superuser = False
        u.is_staff = False
        u.is_active = True

    # tenta preencher email (se existir)
    if hasattr(u, "email") and (not u.email):
        u.email = f"{username}@local"

    u.save()

    # limpa grupos/permissões para "usuário comum"
    if not is_superuser:
        if hasattr(u, "groups"):
            u.groups.clear()
        if hasattr(u, "user_permissions"):
            u.user_permissions.clear()

    return u, created


def main():
    # ===== 1) Usuários =====
    su, created_su = upsert_user(SUPERUSER_USERNAME, PASSWORD, is_superuser=True)
    print(f"[OK] Superuser: {su.username} (created={created_su})")

    for username in USUARIOS:
        u, created = upsert_user(username, PASSWORD, is_superuser=False)
        print(f"[OK] User: {u.username} (created={created})")

    # ===== 2) Modelos do livro =====
    TipoRegistro = get_model("livro_monitoramento", "TipoRegistro")
    Registro = get_model("livro_monitoramento", "Registro")

    if not (TipoRegistro and Registro):
        raise RuntimeError("Não encontrei TipoRegistro/Registro em livro_monitoramento. Verifique o app_label e nomes.")

    tipo_inc, _ = TipoRegistro.objects.get_or_create(nome="Incidente Zabbix", defaults={"ativo": True, "ordem": 1})
    tipo_info, _ = TipoRegistro.objects.get_or_create(nome="Informações", defaults={"ativo": True, "ordem": 2})

    # garante ordem/ativo se já existia
    set_if_field(tipo_inc, "ativo", True)
    set_if_field(tipo_inc, "ordem", 1)
    tipo_inc.save()

    set_if_field(tipo_info, "ativo", True)
    set_if_field(tipo_info, "ordem", 2)
    tipo_info.save()

    # Registros: cria 2 (um por tipo) se ainda não existir com esses títulos
    reg1, created1 = Registro.objects.get_or_create(
        tipo=tipo_inc,
        titulo="INC00012345 - Exemplo de incidente Zabbix",
        defaults={
            "texto": "Alarme de indisponibilidade detectado. Em análise e tratativa. (registro de exemplo)",
            "autor": su,
        },
    )
    reg2, created2 = Registro.objects.get_or_create(
        tipo=tipo_info,
        titulo="Rotina do NOC - Informações gerais",
        defaults={
            "texto": "Checklist rápido: validar alarmes críticos, checar filas de incidentes, atualizar status e registrar no livro.",
            "autor": su,
        },
    )
    print(f"[OK] Registro incidente (created={created1})")
    print(f"[OK] Registro info (created={created2})")

    # ===== 3) Apoio (categorias + itens) =====
    # Ajuste: aqui eu tento encontrar modelos comuns do que vocês criaram na tela:
    # - CategoriaApoio
    # - LinkImportante (ou ApoioItem)
    CategoriaApoio = get_model("livro_monitoramento", "CategoriaApoio")
    LinkImportante = get_model("livro_monitoramento", "LinkImportante") or get_model("livro_monitoramento", "ApoioItem")

    if not CategoriaApoio or not LinkImportante:
        print("[WARN] Não encontrei CategoriaApoio/LinkImportante (ou ApoioItem). Vou pular seed de apoio.")
        return

    cat_plan, _ = CategoriaApoio.objects.get_or_create(nome="Planilhas")
    cat_inf, _ = CategoriaApoio.objects.get_or_create(nome="Informações importantes")

    # Só deixa a categoria “visível” se tiver algo dentro: (isso você controla na view/template)
    # Aqui só garante que existem.

    # Cria 1 item "planilha" (com URL)
    defaults_plan = {}
    # tenta popular campos mais comuns
    for fname, val in [
        ("titulo", "Planilha de Sobreaviso"),
        ("descricao", "Planilha com informações de sobreaviso"),
        ("url", "https://docs.google.com/spreadsheets/d/EXEMPLO"),
        ("conteudo", ""),  # opcional
        ("ordem", 1),
        ("ativo", True),
    ]:
        if any(f.name == fname for f in LinkImportante._meta.fields):
            defaults_plan[fname] = val

    # tenta achar nome do FK da categoria (categoria/categoria_apoio)
    fk_name = None
    for f in LinkImportante._meta.fields:
        if f.is_relation and getattr(f, "related_model", None) == CategoriaApoio:
            fk_name = f.name
            break

    if not fk_name:
        raise RuntimeError("Não encontrei FK de categoria em LinkImportante/ApoioItem.")

    plan_kwargs = {fk_name: cat_plan}
    # chave de unicidade: tenta usar "titulo" + categoria
    if "titulo" in defaults_plan:
        obj_plan, createdp = LinkImportante.objects.get_or_create(**plan_kwargs, titulo=defaults_plan["titulo"], defaults=defaults_plan)
    else:
        obj_plan, createdp = LinkImportante.objects.get_or_create(**plan_kwargs, defaults=defaults_plan)

    print(f"[OK] Apoio planilha (created={createdp})")

    # Cria 1 item de "informação" (com conteúdo)
    defaults_inf = {}
    for fname, val in [
        ("titulo", "Aviso rápido"),
        ("descricao", "Informação útil para o plantão"),
        ("url", ""),  # opcional
        ("conteudo", "Em caso de instabilidade recorrente, registrar no livro e acionar o grupo responsável conforme runbook."),
        ("ordem", 1),
        ("ativo", True),
    ]:
        if any(f.name == fname for f in LinkImportante._meta.fields):
            defaults_inf[fname] = val

    info_kwargs = {fk_name: cat_inf}
    if "titulo" in defaults_inf:
        obj_inf, createdi = LinkImportante.objects.get_or_create(**info_kwargs, titulo=defaults_inf["titulo"], defaults=defaults_inf)
    else:
        obj_inf, createdi = LinkImportante.objects.get_or_create(**info_kwargs, defaults=defaults_inf)

    print(f"[OK] Apoio info (created={createdi})")


if __name__ == "__main__":
    main()

