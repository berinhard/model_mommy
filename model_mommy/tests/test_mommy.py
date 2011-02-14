# -*- coding:utf-8 -*-
from datetime import date, datetime
from decimal import Decimal

from django.db.models.fields import AutoField, CharField, TextField
from django.db.models.fields import DateField, DateTimeField
from django.db.models.fields import IntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField, PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField
from django.db.models.fields import BooleanField

from model_mommy import mommy
from model_mommy.models import Person, Dog, Store
from model_mommy.models import DummyIntModel, DummyPositiveIntModel, DummyNumbersModel
from model_mommy.models import DummyDecimalModel
from model_mommy.generators import gen_from_list

try:
    from django.db.models.fields import BigIntegerField
except ImportError:
    BigIntegerField = IntegerField

from django.test import TestCase

class FieldFillingTestCase(TestCase):

    def setUp(self):
        self.person = mommy.make_one(Person)


class FieldFillingWithParameterTestCase(TestCase):

    def test_simple_creating_person_with_parameters(self):
        kid = mommy.make_one(Person, happy=True, age=10, name='Mike')
        self.assertEqual(kid.age, 10)
        self.assertEqual(kid.happy, True)
        self.assertEqual(kid.name, 'Mike')

    def test_creating_person_from_factory_using_paramters(self):



        person_mom = mommy.Mommy(Person)
        person = person_mom.make_one(happy=False, age=20, gender='M', name='John')
        self.assertEqual(person.age, 20)
        self.assertEqual(person.happy, False)
        self.assertEqual(person.name, 'John')
        self.assertEqual(person.gender, 'M')


class SimpleExtendMommy(TestCase):

    def test_simple_extended_mommy_example(self):
        class Aunt(mommy.Mommy):
            pass

        aunt = Aunt(Person)
        self.cousin = aunt.make_one()


    def test_attr_mapping_with_from_list_generator(self):
        age_list = range(4, 12)

        class KidMommy(mommy.Mommy):
            attr_mapping = {
                'age':gen_from_list(age_list)
            }

        mom = KidMommy(Person)
        kid = mom.make_one()

        # person's age belongs to informed list?
        self.assertTrue(kid.age in age_list)

    def test_type_mapping_overwriting_boolean_model_behavior(self):
        class SadPeopleMommy(mommy.Mommy):
            def __init__(self, model):
                super(SadPeopleMommy, self).__init__(model)
                self.type_mapping.update({
                    BooleanField:lambda:False
                })

        sad_people_mommy = SadPeopleMommy(Person)
        person = sad_people_mommy.make_one()

        # making sure this person is sad >:D
        self.assertEqual(person.happy, False)


class LessSimpleExtendMommy(TestCase):

    def test_fail_no_field_attr_string_to_generator_required(self):
        gen_oposite = lambda x:not x
        gen_oposite.required = ['house']

        class SadPeopleMommy(mommy.Mommy):
            attr_mapping = {'happy':gen_oposite}

        mom = SadPeopleMommy(Person)
        self.assertRaises(AttributeError, lambda:mom.make_one())

    def test_string_to_generator_required(self):
        gen_oposite = lambda default:not default
        gen_oposite.required = ['default']

        class SadPeopleMommy(mommy.Mommy):
            attr_mapping = {'happy':gen_oposite}

        happy_field = Person._meta.get_field('happy')
        mom = SadPeopleMommy(Person)
        person = mom.make_one()
        self.assertEqual(person.happy, not happy_field.default)

    def test_fail_pass_non_string_to_generator_required(self):
        gen_age = lambda x:10

        class MyMommy(mommy.Mommy):
            pass

        MyMommy.attr_mapping = {'age':gen_age}
        mom = MyMommy(Person)

        # for int
        gen_age.required = [10]
        self.assertRaises(ValueError, lambda:mom.make_one())

        # for float
        gen_age.required = [10.10]
        self.assertRaises(ValueError, lambda:mom.make_one())

        # for iterable
        gen_age.required = [[]]
        self.assertRaises(ValueError, lambda:mom.make_one())

        # for iterable/dict
        gen_age.required = [{}]
        self.assertRaises(ValueError, lambda:mom.make_one())

        # for boolean
        gen_age.required = [True]
        self.assertRaises(ValueError, lambda:mom.make_one())

class MommyCreatesSimpleModel(TestCase):

    def test_make_one_should_create_one_object(self):
        person = mommy.make_one(Person)
        self.assertTrue(isinstance(person, Person))

        # makes sure it is the person we created
        self.assertTrue(Person.objects.filter(id=person.id))

    def test_prepare_one_should_not_persist_one_object(self):
        person = mommy.prepare_one(Person)
        self.assertTrue(isinstance(person, Person))

        # makes sure database is clean
        self.assertEqual(Person.objects.all().count(), 0)

        self.assertEqual(person.id, None)


class MommyCreatesAssociatedModels(TestCase):

    def test_dependent_models_with_ForeignKey(self):
        dog = mommy.make_one(Dog)
        self.assertTrue(isinstance(dog.owner, Person))

    def test_prepare_one_should_not_create_one_object(self):
        dog = mommy.prepare_one(Dog)
        self.assertTrue(isinstance(dog, Dog))
        self.assertTrue(isinstance(dog.owner, Person))

        # makes sure database is clean
        self.assertEqual(Person.objects.all().count(), 0)
        self.assertEqual(Dog.objects.all().count(), 0)

    def test_create_many_to_many(self):

        store = mommy.make_one(Store)
        self.assertEqual(store.employees.count(), 5)
        self.assertEqual(store.customers.count(), 5)


class FillNullablesTestCase(TestCase):
    def test_always_fill_nullables_if_value_provided_via_attrs(self):
        bio_data = 'some bio'
        mom = mommy.Mommy(Person, False)
        p = mom.make_one(bio=bio_data)
        self.assertEqual(p.bio, bio_data)

    def test_fill_nullables_if_fill_nullables_is_true(self):
        mom = mommy.Mommy(Person, True)
        p = mom.make_one()
        self.assertTrue( isinstance(p.bio, basestring) )

    def test_do_not_fill_nullables_if_fill_nullables_is_false(self):
        mom = mommy.Mommy(Person, False)
        p = mom.make_one()
        self.assertTrue( p.bio == None )

class FillingFromChoice(FieldFillingTestCase):

    def test_if_gender_is_populated_from_choices(self):
        from model_mommy.models import GENDER_CH
        self.assertTrue(self.person.gender in map(lambda x:x[0], GENDER_CH))


class StringFieldsFilling(FieldFillingTestCase):

    def test_fill_CharField_with_a_random_str(self):
        person_name_field = Person._meta.get_field('name')
        self.assertTrue(isinstance(person_name_field, CharField))

        self.assertTrue(isinstance(self.person.name, str))
        self.assertEqual(len(self.person.name), person_name_field.max_length)

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

    def test_fill_DateField_with_a_date(self):
        appointment_field = Person._meta.get_field('appointment')
        self.assertTrue(isinstance(appointment_field, DateTimeField))

        self.assertTrue(isinstance(self.person.appointment, date))


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
        positive_small_int_field = DummyPositiveIntModel._meta.get_field('positive_small_int_field')
        self.assertTrue(isinstance(positive_small_int_field, PositiveSmallIntegerField))

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
        self.assertTrue(isinstance(self.dummy_numbers_model.float_field, float))

    def test_filling_DecimalField_with_random_decimal(self):
        self.dummy_decimal_model = mommy.make_one(DummyDecimalModel)
        decimal_field = DummyDecimalModel._meta.get_field('decimal_field')

        self.assertTrue(isinstance(decimal_field, DecimalField))
        self.assertTrue(isinstance(self.dummy_decimal_model.decimal_field, basestring))
