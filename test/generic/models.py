#coding: utf-8

#######################################
# TESTING PURPOSE ONLY MODELS!!       #
# DO NOT ADD THE APP TO INSTALLED_APPS#
#######################################
from decimal import Decimal
from tempfile import gettempdir

from django.db import models
from django.core.files.storage import FileSystemStorage

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from .fields import *
from model_mommy.timezone import smart_datetime as datetime

# check whether or not PIL is installed
try:
    from PIL import ImageFile as PilImageFile
except ImportError:
    has_pil = False
else:
    has_pil = True

GENDER_CH = [('M', 'male'), ('F', 'female')]


class ModelWithImpostorField(models.Model):
    pass

class Profile(models.Model):
    email = models.EmailField()

class User(models.Model):
    profile = models.ForeignKey(Profile, blank=True, null=True)


class PaymentBill(models.Model):
    user = models.ForeignKey(User)
    value = models.FloatField()


class Person(models.Model):
    gender = models.CharField(max_length=1, choices=GENDER_CH)
    happy = models.BooleanField(default=True)
    unhappy = models.BooleanField(default=False)
    name = models.CharField(max_length=30)
    nickname = models.SlugField()
    age = models.IntegerField()
    bio = models.TextField()
    birthday = models.DateField()
    birth_time = models.TimeField()
    appointment = models.DateTimeField()
    blog = models.URLField()

    #backward compatibilty with Django 1.1
    try:
        wanted_games_qtd = models.BigIntegerField()
    except AttributeError:
        wanted_games_qtd = models.IntegerField()


class Dog(models.Model):
    owner = models.ForeignKey('Person')
    breed = models.CharField(max_length=50)

class GuardDog(Dog):
    pass

class LonelyPerson(models.Model):
    only_friend = models.OneToOneField(Person)


class Classroom(models.Model):
    students = models.ManyToManyField(Person, null=True)


class Store(models.Model):
    customers = models.ManyToManyField(Person, related_name='favorite_stores')
    employees = models.ManyToManyField(Person, related_name='employers')
    suppliers = models.ManyToManyField(Person, related_name='suppliers', blank=True, null=True)


class DummyIntModel(models.Model):
    int_field = models.IntegerField()
    small_int_field = models.SmallIntegerField()
    try:
        big_int_field = models.BigIntegerField()
    except AttributeError:
        big_int_field = models.IntegerField()


class DummyPositiveIntModel(models.Model):
    positive_small_int_field = models.PositiveSmallIntegerField()
    positive_int_field = models.PositiveIntegerField()


class DummyNumbersModel(models.Model):
    float_field = models.FloatField()


class DummyDecimalModel(models.Model):
    decimal_field = models.DecimalField(max_digits=5, decimal_places=2)


class UnsupportedField(models.Field):
    description = "I'm bad company, mommy doesn't know me"

    def __init__(self, *args, **kwargs):
        super(UnsupportedField, self).__init__(*args, **kwargs)


class UnsupportedModel(models.Model):
    unsupported_field = UnsupportedField()


class DummyEmailModel(models.Model):
    email_field = models.EmailField()


class DummyGenericForeignKeyModel(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class DummyGenericRelationModel(models.Model):
    relation = generic.GenericRelation(DummyGenericForeignKeyModel)


class DummyNullFieldsModel(models.Model):
    null_foreign_key = models.ForeignKey('DummyBlankFieldsModel', null=True)
    null_integer_field = models.IntegerField(null=True)


class DummyBlankFieldsModel(models.Model):
    blank_char_field = models.CharField(max_length=50, blank=True)
    blank_text_field = models.TextField(blank=True)

class DummyDefaultFieldsModel(models.Model):
    default_char_field = models.CharField(max_length=50, default='default')
    default_text_field = models.TextField(default='default')
    default_int_field = models.IntegerField(default=123)
    default_float_field = models.FloatField(default=123.0)
    default_date_field = models.DateField(default='2012-01-01')
    default_date_time_field = models.DateTimeField(default=datetime(2012, 1, 1))
    default_time_field = models.TimeField(default='00:00:00')
    default_decimal_field = models.DecimalField(max_digits=5, decimal_places=2,
                                                default=Decimal('0'))
    default_email_field = models.EmailField(default='foo@bar.org')
    default_slug_field = models.SlugField(default='a-slug')


class DummyFileFieldModel(models.Model):
    fs = FileSystemStorage(location=gettempdir())
    file_field = models.FileField(upload_to="%Y/%m/%d", storage=fs)


if has_pil:
    class DummyImageFieldModel(models.Model):
        fs = FileSystemStorage(location=gettempdir())
        image_field = models.ImageField(upload_to="%Y/%m/%d", storage=fs)
else:
    # doesn't matter, won't be using
    class DummyImageFieldModel(models.Model):
        pass


class DummyMultipleInheritanceModel(DummyDefaultFieldsModel, Person):
    my_dummy_field = models.IntegerField()

class Ambiguous(models.Model):
    name = models.CharField(max_length=20)


class School(models.Model):
    name = models.CharField(max_length = 10)
    students = models.ManyToManyField(Person, through='SchoolEnrollment')


class SchoolEnrollment(models.Model):
    start_date = models.DateField(auto_now_add=True)
    school = models.ForeignKey(School)
    student = models.ForeignKey(Person)

class NonAbstractPerson(Person):
    dummy_count = models.IntegerField()


class CustomFieldWithGeneratorModel(models.Model):
    custom_value = CustomFieldWithGenerator()


class CustomFieldWithoutGeneratorModel(models.Model):
    custom_value = CustomFieldWithoutGenerator()


class DummyUniqueIntegerFieldModel(models.Model):
    value = models.IntegerField(unique=True)
