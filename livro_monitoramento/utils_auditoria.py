def diff_registro(old_obj, new_obj):
    """
    Compara campos relevantes e retorna:
    {"campo": {"old": "...", "new": "..."}, ...}
    """
    fields = ["titulo", "texto"]
    changes = {}

    for f in fields:
        old_v = getattr(old_obj, f, "")
        new_v = getattr(new_obj, f, "")
        if (old_v or "") != (new_v or ""):
            changes[f] = {"old": old_v or "", "new": new_v or ""}

    # tipo (FK)
    old_tipo = getattr(old_obj, "tipo_id", None)
    new_tipo = getattr(new_obj, "tipo_id", None)
    if old_tipo != new_tipo:
        changes["tipo"] = {"old": old_tipo, "new": new_tipo}

    return changes