from django import forms
from .models import Registro, TipoRegistro


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ["tipo", "titulo", "texto"]
        widgets = {
            "titulo": forms.TextInput(attrs={"placeholder": "Ex: INC123456 - Queda Zabbix"}),
            "texto": forms.Textarea(attrs={"rows": 6, "placeholder": "Descreva o ocorrido / evidências / ações..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # só mostra tipos ativos no form
        self.fields["tipo"].queryset = TipoRegistro.objects.filter(ativo=True).order_by("ordem", "nome")
