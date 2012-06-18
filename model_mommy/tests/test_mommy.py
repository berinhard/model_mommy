# -*- coding:utf-8 -*-
from decimal import Decimal

from django.test import TestCase

from model_mommy import mommy
from model_mommy.mommy import ModelNotFound
from model_mommy.models import Person, Dog, Store
from model_mommy.models import UnsupportedModel, DummyGenericRelationModel
from model_mommy.models import DummyNullFieldsModel, DummyBlankFieldsModel
from model_mommy.models import DummyDefaultFieldsModel
from model_mommy.models import DummyGenericForeignKeyModel


class MommyCreatesSimpleModel(TestCase):

    def test_make_one_should_create_one_object(self):
        person = mommy.make_one(Person)
        self.assertIsInstance(person, Person)

        # makes sure it is the person we created
        self.assertTrue(Person.objects.filter(id=person.id))

    def test_prepare_one_should_not_persist_one_object(self):
        person = mommy.prepare_one(Person)
        self.assertIsInstance(person, Person)

        # makes sure database is clean
        self.assertEqual(Person.objects.all().count(), 0)

        self.assertEqual(person.id, None)

    def test_make_many(self):
        people = mommy.make_many(Person, quantity=5)
        self.assertEqual(Person.objects.count(), 5)

        people = mommy.make_many(Person, name="George Washington")
        self.assertTrue(all(p.name == "George Washington" for p in people))

    def test_accept_model_as_string(self):
        person = mommy.make_one('model_mommy.person')
        self.assertIsInstance(person, Person)
        person = mommy.prepare_one('model_mommy.Person')
        self.assertIsInstance(person, Person)
        people = mommy.make_many('model_mommy.person')
        [self.assertIsInstance(person, Person) for person in people]

    def test_raise_pretty_excpetion_if_model_not_found(self):
        with self.assertRaises(ModelNotFound) as context_manager:
            mommy.Mommy('not_existing.Model')
        exception = context_manager.exception

        self.assertEqual(exception.message, "could not find model 'Model' in the app 'not_existing'.")

class MommyCreatesAssociatedModels(TestCase):

    def test_dependent_models_with_ForeignKey(self):
        dog = mommy.make_one(Dog)
        self.assertIsInstance(dog.owner, Person)

    def test_prepare_one_should_not_create_one_object(self):
        dog = mommy.prepare_one(Dog)
        self.assertIsInstance(dog, Dog)
        self.assertIsInstance(dog.owner, Person)

        # makes sure database is clean
        self.assertEqual(Person.objects.all().count(), 0)
        self.assertEqual(Dog.objects.all().count(), 0)

    def test_create_many_to_many(self):

        store = mommy.make_one(Store)
        self.assertEqual(store.employees.count(), 5)
        self.assertEqual(store.customers.count(), 5)

    def test_create_many_to_many_with_set_default_quantity(self):

        mommy.MAX_MANY_QUANTITY = 2

        store = mommy.make_one(Store)
        self.assertEqual(store.employees.count(), 2)
        self.assertEqual(store.customers.count(), 2)

    def test_simple_creating_person_with_parameters(self):
        kid = mommy.make_one(Person, happy=True, age=10, name='Mike')
        self.assertEqual(kid.age, 10)
        self.assertEqual(kid.happy, True)
        self.assertEqual(kid.name, 'Mike')

    def test_creating_person_from_factory_using_paramters(self):
        person_mom = mommy.Mommy(Person)
        person = person_mom.make_one(happy=False, age=20, gender='M',
                                     name='John')
        self.assertEqual(person.age, 20)
        self.assertEqual(person.happy, False)
        self.assertEqual(person.name, 'John')
        self.assertEqual(person.gender, 'M')


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
        self.assertIsInstance(dummy, DummyGenericRelationModel)


class HandlingContentTypeField(TestCase):
    def test_create_model_with_contenttype_field(self):
        dummy = mommy.make_one(DummyGenericForeignKeyModel)
        self.assertIsInstance(dummy, DummyGenericForeignKeyModel)


class SkipNullsTestCase(TestCase):
    def test_skip_null(self):
        dummy = mommy.make_one(DummyNullFieldsModel)
        self.assertEqual(dummy.null_foreign_key, None)
        self.assertEqual(dummy.null_integer_field, None)


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
        self.assertEqual(dummy.default_time_field, '00:00:00')
        self.assertEqual(dummy.default_decimal_field, Decimal('0'))
        self.assertEqual(dummy.default_email_field, 'foo@bar.org')
        self.assertEqual(dummy.default_slug_field, 'a-slug')
