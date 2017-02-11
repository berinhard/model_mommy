#coding: utf-8

#######################################
# TESTING PURPOSE ONLY MODELS!!       #
# DO NOT ADD THE APP TO INSTALLED_APPS#
#######################################
from decimal import Decimal
from tempfile import gettempdir

from django import VERSION
from django.db import models
from django.core.files.storage import FileSystemStorage

from django.contrib.contenttypes.models import ContentType
if VERSION >= (1, 7):
    from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
else:
    from django.contrib.contenttypes.generic import GenericRelation, GenericForeignKey

from .fields import *
from model_mommy.timezone import smart_datetime as datetime
import datetime as base_datetime

# check whether or not PIL is installed
try:
    from PIL import ImageFile as PilImageFile
except ImportError:
    has_pil = False
else:
    has_pil = True

GENDER_CH = [('M', 'male'), ('F', 'female')]

OCCUPATION_CHOCIES = (
    ('Service Industry', (
        ('waitress', 'Waitress'),
        ('bartender', 'Bartender'))),
    ('Education', (
        ('teacher', 'Teacher'),
        ('principal', 'Principal'))))

TEST_TIME = base_datetime.datetime(2014, 7, 21, 15, 39, 58, 457698)


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
    bipolar = models.BooleanField(default=False)
    name = models.CharField(max_length=30)
    nickname = models.SlugField(max_length=36)
    age = models.IntegerField()
    bio = models.TextField()
    birthday = models.DateField()
    birth_time = models.TimeField()
    appointment = models.DateTimeField()
    blog = models.URLField()
    occupation = models.CharField(max_length=10, choices=OCCUPATION_CHOCIES)
    try:
        uuid = models.UUIDField(primary_key=False)
    except AttributeError:
        # New at Django 1.9
        pass
    try:
        name_hash = models.BinaryField(max_length=16)
    except AttributeError:
        # We can't test the binary field if it is not supported
        # (django < 1,6)
        pass
    try:
        from django.contrib.postgres.fields import ArrayField
        acquaintances = ArrayField(models.IntegerField())
    except ImportError:
        # New at Django 1.9
        pass

    try:
        from django.contrib.postgres.fields import JSONField
        data = JSONField()
    except ImportError:
        # New at Django 1.9
        pass

    try:
        from django.contrib.postgres.fields import HStoreField
        hstore_data = HStoreField()
    except ImportError:
        # New at Django 1.8
        pass

    #backward compatibilty with Django 1.1
    try:
        wanted_games_qtd = models.BigIntegerField()
    except AttributeError:
        wanted_games_qtd = models.IntegerField()

    try:
        duration_of_sleep = models.DurationField()
    except AttributeError:
        pass


class Dog(models.Model):

    class Meta:
        order_with_respect_to = 'owner'

    owner = models.ForeignKey('Person')
    breed = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    friends_with = models.ManyToManyField('Dog')

class GuardDog(Dog):
    pass

class LonelyPerson(models.Model):
    only_friend = models.OneToOneField(Person)


class RelatedNamesModel(models.Model):
    name = models.CharField(max_length=256)
    one_to_one = models.OneToOneField(Person, related_name='one_related')
    foreign_key = models.ForeignKey(Person, related_name='fk_related')


class ModelWithOverridedSave(Dog):

    def save(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        return super(ModelWithOverridedSave, self).save(*args, **kwargs)


class Classroom(models.Model):
    students = models.ManyToManyField(Person, null=True)


class Store(models.Model):
    customers = models.ManyToManyField(Person, related_name='favorite_stores')
    employees = models.ManyToManyField(Person, related_name='employers')
    suppliers = models.ManyToManyField(Person, related_name='suppliers', blank=True, null=True)

class DummyEmptyModel(models.Model):
    pass

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
    decimal_field = models.DecimalField(max_digits=1, decimal_places=0)


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
    content_object = GenericForeignKey('content_type', 'object_id')


class DummyGenericRelationModel(models.Model):
    relation = GenericRelation(DummyGenericForeignKeyModel)


class DummyNullFieldsModel(models.Model):
    null_foreign_key = models.ForeignKey('DummyBlankFieldsModel', null=True)
    null_integer_field = models.IntegerField(null=True)


class DummyBlankFieldsModel(models.Model):
    blank_char_field = models.CharField(max_length=50, blank=True)
    blank_text_field = models.TextField(max_length=300, blank=True)

class DummyDefaultFieldsModel(models.Model):
    default_id = models.AutoField(primary_key=True)
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
    my_id = models.AutoField(primary_key=True)
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


class CustomForeignKeyWithGeneratorModel(models.Model):
    custom_fk = CustomForeignKey(Profile, blank=True, null=True)


class DummyUniqueIntegerFieldModel(models.Model):
    value = models.IntegerField(unique=True)


class ModelWithNext(models.Model):
    attr = models.CharField(max_length=10)

    def next(self):
        return 'foo'


class BaseModelForNext(models.Model):
    fk = models.ForeignKey(ModelWithNext)


class BaseModelForList(models.Model):
    fk = FakeListField()

class Movie(models.Model):
    title = models.CharField(max_length=30)

class CastMember(models.Model):
    movie = models.ForeignKey(Movie, related_name='cast_members')
    person = models.ForeignKey(Person)

if VERSION < (1, 4):
    class DummyIPAddressFieldModel(models.Model):
        ipv4_field = models.IPAddressField()  # Deprecated in Django 1.7
else:
    class DummyGenericIPAddressFieldModel(models.Model):
        ipv4_field = models.GenericIPAddressField(protocol='IPv4')
        ipv6_field = models.GenericIPAddressField(protocol='IPv6')
        ipv46_field = models.GenericIPAddressField(protocol='both')
