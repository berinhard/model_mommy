from datetime import date, datetime
from decimal import Decimal

import os
from os.path import abspath, join, dirname

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import CharField, TextField, SlugField
from django.db.models.fields import DateField, DateTimeField, EmailField
from django.db.models.fields import IntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField
from django.db.models.fields import BooleanField, URLField
from django.db.models import FileField
from django.core.files import File

try:
    from django.db.models.fields import BigIntegerField
except ImportError:
    pass
    #BigIntegerField = IntegerField

from model_mommy import mommy
from model_mommy.models import Person
from model_mommy.models import DummyIntModel, DummyPositiveIntModel
from model_mommy.models import DummyNumbersModel
from model_mommy.models import DummyDecimalModel, DummyEmailModel
from model_mommy.models import DummyGenericForeignKeyModel
from model_mommy.models import DummyFileFieldModel

__all__ = [
    'StringFieldsFilling', 'BooleanFieldsFilling', 'DateTimeFieldsFilling',
    'DateFieldsFilling', 'FillingIntFields', 'FillingPositiveIntFields',
    'FillingOthersNumericFields', 'FillingFromChoice', 'URLFieldsFilling',
    'FillingEmailField', 'FillingGenericForeignKeyField','FillingFileField',
]


def assert_not_raise(method, parameters, exception):
    try:
        method(*parameters)
    except exception:
        msg = "Exception %s not expected to be raised" % exception.__name__
        raise AssertionError(msg)


class FieldFillingTestCase(TestCase):

    def setUp(self):
        self.person = mommy.make_one(Person)


class FillingFromChoice(FieldFillingTestCase):

    def test_if_gender_is_populated_from_choices(self):
        from model_mommy.models import GENDER_CH
        self.assertTrue(self.person.gender in map(lambda x: x[0], GENDER_CH))


class StringFieldsFilling(FieldFillingTestCase):

    def test_fill_CharField_with_a_random_str(self):
        person_name_field = Person._meta.get_field('name')
        self.assertTrue(isinstance(person_name_field, CharField))

        self.assertTrue(isinstance(self.person.name, str))
        self.assertEqual(len(self.person.name), person_name_field.max_length)

    def test_fill_SlugField_with_a_random_str(self):
        person_nickname_field = Person._meta.get_field('nickname')
        self.assertTrue(isinstance(person_nickname_field, SlugField))

        self.assertTrue(isinstance(self.person.nickname, str))
        self.assertEqual(len(self.person.nickname),
                         person_nickname_field.max_length)

    def test_fill_TextField_with_a_random_str(self):
        person_bio_field = Person._meta.get_field('bio')
        self.assertTrue(isinstance(person_bio_field, TextField))

        self.assertTrue(isinstance(self.person.bio, str))


class BooleanFieldsFilling(FieldFillingTestCase):
    def test_fill_BooleanField_with_boolean(self):
        happy_field = Person._meta.get_field('happy')
        self.assertTrue(isinstance(happy_field, BooleanField))

        self.assertTrue(isinstance(self.person.happy, bool))


class DateFieldsFilling(FieldFillingTestCase):

    def test_fill_DateField_with_a_date(self):
        birthday_field = Person._meta.get_field('birthday')
        self.assertTrue(isinstance(birthday_field, DateField))

        self.assertTrue(isinstance(self.person.birthday, date))


class DateTimeFieldsFilling(FieldFillingTestCase):

    def test_fill_DateTimeField_with_a_datetime(self):
        appointment_field = Person._meta.get_field('appointment')
        self.assertTrue(isinstance(appointment_field, DateTimeField))

        self.assertTrue(isinstance(self.person.appointment, datetime))


class FillingIntFields(TestCase):

    def setUp(self):
        self.dummy_int_model = mommy.make_one(DummyIntModel)

    def test_fill_IntegerField_with_a_random_number(self):
        int_field = DummyIntModel._meta.get_field('int_field')
        self.assertTrue(isinstance(int_field, IntegerField))

        self.assertTrue(isinstance(self.dummy_int_model.int_field, int))

    def test_fill_BigIntegerField_with_a_random_number(self):
        big_int_field = DummyIntModel._meta.get_field('big_int_field')
        self.assertTrue(isinstance(big_int_field, BigIntegerField))

        self.assertTrue(isinstance(self.dummy_int_model.big_int_field, int))

    def test_fill_SmallIntegerField_with_a_random_number(self):

        small_int_field = DummyIntModel._meta.get_field('small_int_field')
        self.assertTrue(isinstance(small_int_field, SmallIntegerField))

        self.assertTrue(isinstance(self.dummy_int_model.small_int_field, int))


class FillingPositiveIntFields(TestCase):

    def setUp(self):
        self.dummy_positive_int_model = mommy.make_one(DummyPositiveIntModel)

    def test_fill_PositiveSmallIntegerField_with_a_random_number(self):
        field = DummyPositiveIntModel._meta.get_field('positive_small_int_field')
        positive_small_int_field = field
        self.assertTrue(isinstance(positive_small_int_field,
                        PositiveSmallIntegerField))

        self.assertTrue(isinstance(self.dummy_positive_int_model.positive_small_int_field, int))
        self.assertTrue(self.dummy_positive_int_model.positive_small_int_field > 0)

    def test_fill_PositiveIntegerField_with_a_random_number(self):
        positive_int_field = DummyPositiveIntModel._meta.get_field('positive_int_field')
        self.assertTrue(isinstance(positive_int_field, PositiveIntegerField))

        self.assertTrue(isinstance(self.dummy_positive_int_model.positive_int_field, int))
        self.assertTrue(self.dummy_positive_int_model.positive_int_field > 0)


class FillingOthersNumericFields(TestCase):
    def test_filling_FloatField_with_a_random_float(self):
        self.dummy_numbers_model = mommy.make_one(DummyNumbersModel)
        float_field = DummyNumbersModel._meta.get_field('float_field')
        self.assertTrue(isinstance(float_field, FloatField))
        self.assertTrue(isinstance(self.dummy_numbers_model.float_field,
                                   float))

    def test_filling_DecimalField_with_random_decimal(self):
        self.dummy_decimal_model = mommy.make_one(DummyDecimalModel)
        decimal_field = DummyDecimalModel._meta.get_field('decimal_field')

        self.assertTrue(isinstance(decimal_field, DecimalField))
        self.assertTrue(isinstance(self.dummy_decimal_model.decimal_field,
                                   Decimal))


class URLFieldsFilling(FieldFillingTestCase):

    def test_fill_URLField_with_valid_url(self):
        blog_field = Person._meta.get_field('blog')
        self.assertTrue(isinstance(blog_field, URLField))

        self.assertTrue(isinstance(self.person.blog, str))


class FillingEmailField(TestCase):

    def test_filling_EmailField(self):
        obj = mommy.make_one(DummyEmailModel)
        field = DummyEmailModel._meta.get_field('email_field')
        self.assertTrue(isinstance(field, EmailField))
        self.assertTrue(isinstance(obj.email_field, basestring))


class FillingGenericForeignKeyField(TestCase):

    def test_filling_content_type_field(self):
        dummy = mommy.make_one(DummyGenericForeignKeyModel)
        self.assertTrue(isinstance(dummy.content_type, ContentType))

class FillingFileField(TestCase):

    def setUp(self):
        path = abspath(join(dirname(__file__),'..','mock_file.txt'))
        self.fixture_txt_file = File(open(path))

    def test_filling_file_field(self):
        self.dummy = mommy.make_one(DummyFileFieldModel)
        field = DummyFileFieldModel._meta.get_field('file_field')

        self.assertTrue(isinstance(field,FileField))

        import time
        path = "/tmp/%s/mock_file.txt" % time.strftime('%Y/%m/%d')

        self.assertEqual(self.dummy.file_field.path, path)

    def tearDown(self):
        self.dummy.file_field.delete()

