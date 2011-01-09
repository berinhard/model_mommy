#coding: utf-8
from django.db.models.fields import AutoField, CharField, TextField
from django.db.models.fields import DateField
from django.db.models.fields import IntegerField, BigIntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField, PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField

from django.db.models import ForeignKey
from string import letters
from random import choice, randint
from datetime import date
from decimal import Decimal

MAX_LENGTH = 100
MAX_INT_VALUE = 1000

INT_FIELDS = (
    IntegerField, BigIntegerField, SmallIntegerField,
    PositiveIntegerField, PositiveSmallIntegerField,
)

STR_FIELDS = (CharField, TextField)

def make_one(model):
    attrs = {}
    for field in model._meta.fields:
        if isinstance(model, AutoField):
            continue
        attrs[field.name] = _generate_value(field)
    return model.objects.create(**attrs)


def _generate_value(field):
    if isinstance(field, STR_FIELDS):
        random_str = ''
        for i in range(field.max_length or MAX_LENGTH):
            random_str += choice(letters)
        return random_str
    elif isinstance(field, INT_FIELDS):
        return randint(1, MAX_INT_VALUE)
    elif isinstance(field, FloatField):
        return float(randint(1, MAX_INT_VALUE))
    elif isinstance(field, ForeignKey):
        return make_one(field.related.parent_model)
    elif isinstance(field, DateField):
        return date.today()
