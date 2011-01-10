# -*- coding:utf-8 -*-
from datetime import date, datetime
from decimal import Decimal

from django.db.models.fields import *
from django.test import TestCase

class FieldFillingTestCase(TestCase):

    def setUp(self):
        from model_mommy import mommy
        from model_mommy.models import Kid
        
        self.kid = mommy.make_one(Kid)

class MommyCreatesSimpleModel(TestCase):

    def test_make_one_should_create_one_object(self):
        from model_mommy import mommy
        from model_mommy.models import Kid
        
        kid = mommy.make_one(Kid)
        self.assertTrue(isinstance(kid, Kid))
        self.assertEqual(Kid.objects.all().count(), 1)

class MommyCreatesAssociatedModels(TestCase):
    def test_dependent_models_with_ForeignKey(self):
        from model_mommy import mommy
        from model_mommy.models import Dog, Kid
        
        dog = mommy.make_one(Dog)
        self.assertTrue(isinstance(dog.owner, Kid))

class StringFieldsFilling(FieldFillingTestCase):

    def test_fill_CharField_with_a_random_str(self):
        from model_mommy.models import Kid
        
        kid_name_field = Kid._meta.get_field('name')
        self.assertTrue(isinstance(kid_name_field, CharField))

        self.assertTrue(isinstance(self.kid.name, str))
        self.assertEqual(len(self.kid.name), kid_name_field.max_length)

    def test_fill_TextField_with_a_random_str(self):
        from model_mommy.models import Kid
        
        kid_bio_field = Kid._meta.get_field('bio')
        self.assertTrue(isinstance(kid_bio_field, TextField))

        self.assertTrue(isinstance(self.kid.bio, str))

class BooleanFieldsFilling(FieldFillingTestCase):
    def test_fill_BooleanField_with_boolean(self):
        from model_mommy.models import Kid
        
        happy_field = Kid._meta.get_field('happy')
        self.assertTrue(isinstance(happy_field, BooleanField))
        
        self.assertTrue(isinstance(self.kid.happy, bool))

class DateFieldsFilling(FieldFillingTestCase):

    def test_fill_DateField_with_a_date(self):
        from model_mommy.models import Kid
        
        birthday_field = Kid._meta.get_field('birthday')
        self.assertTrue(isinstance(birthday_field, DateField))
        
        self.assertTrue(isinstance(self.kid.birthday, date))        
        
class DateTimeFieldsFilling(FieldFillingTestCase):

    def test_fill_DateField_with_a_date(self):
        from model_mommy.models import Kid
        
        appointment_field = Kid._meta.get_field('appointment')
        self.assertTrue(isinstance(appointment_field, DateTimeField))
        
        self.assertTrue(isinstance(self.kid.appointment, date))


class FillingIntFields(TestCase):

    def setUp(self):
        from model_mommy import mommy
        from model_mommy.models import DummyIntModel
        
        self.dummy_int_model = mommy.make_one(DummyIntModel)

    def test_fill_IntegerField_with_a_random_number(self):
        from model_mommy.models import DummyIntModel
        
        int_field = DummyIntModel._meta.get_field('int_field')
        self.assertTrue(isinstance(int_field, IntegerField))

        self.assertTrue(isinstance(self.dummy_int_model.int_field, int))

    def test_fill_BigIntegerField_with_a_random_number(self):
        from model_mommy.models import DummyIntModel
        
        big_int_field = DummyIntModel._meta.get_field('big_int_field')
        self.assertTrue(isinstance(big_int_field, BigIntegerField))

        self.assertTrue(isinstance(self.dummy_int_model.big_int_field, int))

    def test_fill_SmallIntegerField_with_a_random_number(self):
        from model_mommy.models import DummyIntModel
        
        small_int_field = DummyIntModel._meta.get_field('small_int_field')
        self.assertTrue(isinstance(small_int_field, SmallIntegerField))

        self.assertTrue(isinstance(self.dummy_int_model.small_int_field, int))


class FillingPositiveIntFields(TestCase):
    
    def setUp(self):
        from model_mommy import mommy
        from model_mommy.models import DummyPositiveIntModel
        
        self.dummy_positive_int_model = mommy.make_one(DummyPositiveIntModel)
    
    def test_fill_PositiveSmallIntegerField_with_a_random_number(self):
        from model_mommy.models import DummyPositiveIntModel
        
        positive_small_int_field = DummyPositiveIntModel._meta.get_field('positive_small_int_field')
        self.assertTrue(isinstance(positive_small_int_field, PositiveSmallIntegerField))

        self.assertTrue(isinstance(self.dummy_positive_int_model.positive_small_int_field, int))
        self.assertTrue(self.dummy_positive_int_model.positive_small_int_field > 0)

    def test_fill_PositiveIntegerField_with_a_random_number(self):
        from model_mommy.models import DummyPositiveIntModel
        
        positive_int_field = DummyPositiveIntModel._meta.get_field('positive_int_field')
        self.assertTrue(isinstance(positive_int_field, PositiveIntegerField))

        self.assertTrue(isinstance(self.dummy_positive_int_model.positive_int_field, int))
        self.assertTrue(self.dummy_positive_int_model.positive_int_field > 0)

class FillingOthersNumericFields(TestCase):
    def test_filling_FloatField_with_a_random_float(self):
        from model_mommy import mommy
        from model_mommy.models import DummyNumbersModel
        
        self.dummy_numbers_model = mommy.make_one(DummyNumbersModel)
        float_field = DummyNumbersModel._meta.get_field('float_field')
        self.assertTrue(isinstance(float_field, FloatField))
        self.assertTrue(isinstance(self.dummy_numbers_model.float_field, float))

    def test_filling_DecimalField_with_random_decimal(self):
        from model_mommy import mommy
        from model_mommy.models import DummyDecimalModel
        
        self.dummy_decimal_model = mommy.make_one(DummyDecimalModel)
        decimal_field = DummyDecimalModel._meta.get_field('decimal_field')
        
        self.assertTrue(isinstance(decimal_field, DecimalField))
        self.assertTrue(isinstance(self.dummy_decimal_model.decimal_field, basestring))
