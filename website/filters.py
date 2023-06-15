import django_filters
from django_filters.widgets import LinkWidget

from .models import *

CatalogSort = [
    ["title", "Название (по возрастанию)"],
    ["-title", "Название (по убыванию)"],
    ["cost", "Цена (по возрастанию)"],
    ["-cost", "Цена (по убыванию)"],
]


class CatalogFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Название")
    category = django_filters.ChoiceFilter(label='Категория', choices=list(Category.objects.all().values_list('id', 'title')))
    brand = django_filters.ChoiceFilter(label='Бренд', choices=list(Brand.objects.all().values_list('id', 'title')))
    ordering = django_filters.OrderingFilter(choices=CatalogSort, required=False, empty_label=None, label="Сортировка")

    class Meta:
        model = Product
        fields = ['title']
        order_by_field = 'title'


ProcedureSort = [
    ["title", "Название (по возрастанию)"],
    ["-title", "Название (по убыванию)"],
    ["cost", "Цена (по возрастанию)"],
    ["-cost", "Цена (по убыванию)"],
]


class ProcedureFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Название")
    # category = django_filters.ChoiceFilter(label='Категория', choices=list(Category.objects.all().values_list('id', 'title')))
    # brand = django_filters.ChoiceFilter(label='Бренд', choices=list(Brand.objects.all().values_list('id', 'title')))
    ordering = django_filters.OrderingFilter(choices=ProcedureSort, required=False, empty_label=None, label="Сортировка")

    class Meta:
        model = Product
        fields = ['title']
        order_by_field = 'title'


RequestSort = [
    ["begin_date", "Дата процедуры (по возрастанию)"],
    ["-begin_date", "Дата процедуры (по убыванию)"],
    ["completed", "Обработано (по возрастанию)"],
    ["-completed", "Обработано (по убыванию)"],
]


class RequestFilter(django_filters.FilterSet):
    # title = django_filters.CharFilter(lookup_expr='icontains', label="Название")
    procedure = django_filters.ChoiceFilter(label='Процедура', choices=list(Procedure.objects.all().values_list('id', 'title')))
    # с = django_filters.ChoiceFilter(label='Бренд', choices=list(Brand.objects.all().values_list('id', 'title')))
    ordering = django_filters.OrderingFilter(choices=RequestSort, required=False, empty_label=None, label="Сортировка")

    class Meta:
        model = Request
        fields = ['begin_date']
        order_by_field = 'begin_date'