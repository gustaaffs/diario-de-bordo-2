from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from .models import Registro, LogAcao
from .utils_auditoria import diff_registro


@receiver(pre_save, sender=Registro)
def registro_pre_save(sender, instance, **kwargs):
    # guarda o "antes" para diff no post_save
    if instance.pk:
        try:
            instance._old = Registro.objects.get(pk=instance.pk)
        except Registro.DoesNotExist:
            instance._old = None
    else:
        instance._old = None


@receiver(post_save, sender=Registro)
def registro_post_save(sender, instance, created, **kwargs):
    if created:
        LogAcao.objects.create(
            usuario=getattr(instance, "autor", None),
            acao="CREATE",
            tipo=getattr(instance, "tipo", None),
            registro_id=instance.pk,
            titulo=getattr(instance, "titulo", "") or "",
            detalhes={},
        )
    else:
        old_obj = getattr(instance, "_old", None)
        if not old_obj:
            return
        changes = diff_registro(old_obj, instance)
        if changes:
            LogAcao.objects.create(
                usuario=getattr(instance, "autor", None),  # ou request.user (melhor: ver nota abaixo)
                acao="UPDATE",
                tipo=getattr(instance, "tipo", None),
                registro_id=instance.pk,
                titulo=getattr(instance, "titulo", "") or "",
                detalhes=changes,
            )


@receiver(post_delete, sender=Registro)
def registro_post_delete(sender, instance, **kwargs):
    LogAcao.objects.create(
        usuario=getattr(instance, "autor", None),
        acao="DELETE",
        tipo=getattr(instance, "tipo", None),
        registro_id=getattr(instance, "pk", None),
        titulo=getattr(instance, "titulo", "") or "",
        detalhes={},
    )