# -*- coding:utf-8 -*-
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy
from model_mommy.models import Person, Dog, Store
from model_mommy.models import UnsupportedModel, DummyGenericRelationModel
from model_mommy.models import DummyBlankFieldsModel, DummyDefaultFieldsModel, DummyGenericForeignKeyModel

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

class HandlingUnsupportedModels(TestCase):
    def test_unsupported_model_raises_an_explanatory_exception(self):
        try:
            mommy.make_one(UnsupportedModel)
            self.fail("Should have raised a TypeError")
        except TypeError, e:
            self.assertTrue('not supported' in repr(e))

class HandlingModelsWithGenericRelationFields(TestCase):
    def test_create_model_with_generic_relation(self):
        dummy = mommy.make_one(DummyGenericRelationModel)
        self.assertTrue(isinstance(dummy, DummyGenericRelationModel))

class HandlingContentTypeField(TestCase):
    def test_create_model_with_contenttype_field(self):
        dummy = mommy.make_one(DummyGenericForeignKeyModel)
        self.assertTrue(isinstance(dummy, DummyGenericForeignKeyModel))


class SkipBlanksTestCase(TestCase):
    def test_skip_blank(self):
        dummy = mommy.make_one(DummyBlankFieldsModel)
        self.assertEqual(dummy.blank_char_field, '')
        self.assertEqual(dummy.blank_text_field, '')

class SkipDefaultsTestCase(TestCase):
    def test_skip_fields_with_default(self):
        dummy = mommy.make_one(DummyDefaultFieldsModel)
        self.assertEqual(dummy.default_char_field, 'default')
        self.assertEqual(dummy.default_text_field, 'default')
        self.assertEqual(dummy.default_int_field, 123)
        self.assertEqual(dummy.default_float_field, 123.0)
        self.assertEqual(dummy.default_date_field, '2011-01-01')
        self.assertEqual(dummy.default_date_time_field, '2011-01-01')
        self.assertEqual(dummy.default_decimal_field, Decimal('0'))
        self.assertEqual(dummy.default_email_field, 'foo@bar.org')
        self.assertEqual(dummy.default_slug_field, 'a-slug')
