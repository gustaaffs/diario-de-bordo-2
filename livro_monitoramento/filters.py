import django_filters
from django import forms
from django.db.models import Q

from .models import Registro, TipoRegistro, LogAcao


class RegistroFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q", label="Busca")

    tipo = django_filters.ModelChoiceFilter(
        queryset=TipoRegistro.objects.filter(ativo=True).order_by("ordem", "nome"),
        empty_label="---------",
        label="Tipo"
    )

    de = django_filters.DateFilter(
        field_name="criado_em",
        lookup_expr="date__gte",
        label="De",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    ate = django_filters.DateFilter(
        field_name="criado_em",
        lookup_expr="date__lte",
        label="Até",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    def filter_q(self, queryset, name, value):
        if not value:
            return queryset
        value = value.strip()
        return queryset.filter(
            Q(titulo__icontains=value) |
            Q(texto__icontains=value) |
            Q(autor__username__icontains=value) |
            Q(autor__first_name__icontains=value) |
            Q(autor__last_name__icontains=value)
        )

    class Meta:
        model = Registro
        fields = ["q", "tipo", "de", "ate"]

class LogAcaoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q", label="")

    de = django_filters.DateFilter(
        field_name="criado_em", lookup_expr="date__gte",
        widget=forms.DateInput(attrs={"type":"date", "class":"input input-date"})
    )
    ate = django_filters.DateFilter(
        field_name="criado_em", lookup_expr="date__lte",
        widget=forms.DateInput(attrs={"type":"date", "class":"input input-date"})
    )

    class Meta:
        model = LogAcao
        fields = ["tipo", "de", "ate"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # deixa o select do tipo no padrão da toolbar
        if "tipo" in self.form.fields:
            self.form.fields["tipo"].widget.attrs.update({"class": ""})  # se você já estiliza select globalmente

    def filter_q(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            django_filters.filters.Q(titulo__icontains=value) |
            django_filters.filters.Q(usuario__username__icontains=value) |
            django_filters.filters.Q(usuario__first_name__icontains=value) |
            django_filters.filters.Q(usuario__last_name__icontains=value)
        )