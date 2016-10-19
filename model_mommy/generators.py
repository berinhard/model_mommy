import random_gen
from .random_gen import *

import django
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    CharField, EmailField, SlugField, TextField, URLField,
    DateField, DateTimeField, TimeField,
    AutoField, IntegerField, SmallIntegerField,
    PositiveIntegerField, PositiveSmallIntegerField,
    BooleanField, DecimalField, FloatField,
    FileField, ImageField, Field, IPAddressField,
    ForeignKey, ManyToManyField, OneToOneField)
if django.VERSION >= (1, 9):
    from django.db.models.fields.related import ReverseManyToOneDescriptor as ForeignRelatedObjectsDescriptor
else:
    from django.db.models.fields.related import ForeignRelatedObjectsDescriptor
from django.db.models.fields.proxy import OrderWrt
try:
    from django.db.models import BigIntegerField
except ImportError:
    BigIntegerField = IntegerField

try:
    from django.db.models import GenericIPAddressField
except ImportError:
    GenericIPAddressField = IPAddressField

try:
    from django.db.models import BinaryField
except ImportError:
    BinaryField = None

try:
    from django.db.models import DurationField
except ImportError:
    DurationField = None

try:
    from django.db.models import UUIDField
except ImportError:
    UUIDField = None

try:
    from django.contrib.postgres.fields import ArrayField
except ImportError:
    ArrayField = None

try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    JSONField = None


default_mapping = {
    BooleanField: random_gen.gen_boolean,
    IntegerField: random_gen.gen_integer,
    BigIntegerField: random_gen.gen_integer,
    SmallIntegerField: random_gen.gen_integer,

    PositiveIntegerField: lambda: random_gen.gen_integer(0),
    PositiveSmallIntegerField: lambda: random_gen.gen_integer(0),

    FloatField: random_gen.gen_float,
    DecimalField: random_gen.gen_decimal,

    CharField: random_gen.gen_string,
    TextField: random_gen.gen_text,
    SlugField: random_gen.gen_slug,

    DateField: random_gen.gen_date,
    DateTimeField: random_gen.gen_datetime,
    TimeField: random_gen.gen_time,

    URLField: random_gen.gen_url,
    EmailField: random_gen.gen_email,
    IPAddressField: random_gen.gen_ipv4,
    FileField: random_gen.gen_file_field,
    ImageField: random_gen.gen_image_field,

    ContentType: random_gen.gen_content_type,
}

if BinaryField:
    default_mapping[BinaryField] = random_gen.gen_byte_string
if DurationField:
    default_mapping[DurationField] = random_gen.gen_interval
if UUIDField:
    default_mapping[UUIDField] = random_gen.gen_uuid
if ArrayField:
    default_mapping[ArrayField] = random_gen.gen_array
if JSONField:
    default_mapping[JSONField] = random_gen.gen_json


def get_type_mapping():
    from .mommy import make, _m2m_generator

    mapping = default_mapping.copy()
    mapping[ForeignKey] = make
    mapping[OneToOneField] = make
    mapping[ManyToManyField] = _m2m_generator

    return mapping.copy()
