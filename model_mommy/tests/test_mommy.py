# -*- coding:utf-8 -*-
from import_helpers import *
from django.test import TestCase


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

