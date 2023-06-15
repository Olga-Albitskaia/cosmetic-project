import datetime
import os

import django
from django.forms import Select
from website.models import *


class LoadFromFileForm(django.forms.Form):
    format = django.forms.ChoiceField(label='База данных', choices=[
        ('', 'Не выбрано'),
        (1, 'Excel'),
        (2, 'CSV'),
    ])
    file = django.forms.FileField (label='Файл')


class LoadFromDbForm(django.forms.Form):
    db = django.forms.ChoiceField(label='База данных', choices=[
                ('', 'Не выбрано'),
                (1, 'PostgreSQL'),
                (2, 'MySQL'),
            ])
    host = django.forms.CharField(label='Хост', max_length=255)
    port = django.forms.IntegerField(label='Порт')
    login = django.forms.CharField(label='Логин', max_length=255)
    password = django.forms.CharField(label='Пароль', max_length=255)
    db_name = django.forms.CharField(label='База данных', max_length=255)
    db_table = django.forms.CharField(label='Таблица', max_length=255)


class LoadResultForm(django.forms.Form):
    message = django.forms.CharField(label='Результат загрузки', widget=django.forms.Textarea)


class UserProfileForm(django.forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'middle_name', 'gender', 'birthday', 'email', 'phone', 'address']


class ReportSettingsForm(django.forms.ModelForm):
    class Meta:
        model = User
        fields = ['report_date_1', 'report_date_2']

