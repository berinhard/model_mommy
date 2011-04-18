# -*- coding:utf-8 -*-
from datetime import date, datetime
from decimal import Decimal

from django.db.models.fields import AutoField, CharField, TextField, SlugField
from django.db.models.fields import DateField, DateTimeField, EmailField
from django.db.models.fields import IntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField, PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField
from django.db.models.fields import BooleanField, URLField

from model_mommy import mommy
from model_mommy.models import Person, Dog, Store, ModelWithSelfReference
from model_mommy.models import DummyIntModel, DummyPositiveIntModel, DummyNumbersModel
from model_mommy.models import DummyDecimalModel, UnsupportedModel, DummyEmailModel
from model_mommy.models import DummyGenericRelationModel, DummyBlankFieldsModel, DummyDefaultFieldsModel
from model_mommy.generators import gen_from_list

try:
    from django.db.models.fields import BigIntegerField
except ImportError:
    BigIntegerField = IntegerField
