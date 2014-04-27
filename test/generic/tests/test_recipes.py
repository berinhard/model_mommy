#coding: utf-8

import itertools
from random import choice
from mock import patch
from decimal import Decimal
from django.test import TestCase
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key, RecipeForeignKey
from model_mommy.timezone import now
from model_mommy.exceptions import InvalidQuantityException, RecipeIteratorEmpty
from test.generic.models import Person, DummyNumbersModel, DummyBlankFieldsModel, Dog


class TestDefiningRecipes(TestCase):
    def setUp(self):
        self.recipe_attrs = {
          'name': 'John Doe',
          'nickname': 'joe',
          'age': 18,
          'bio': 'Someone in the crowd',
          'birthday': now().date(),
          'appointment': now(),
          'blog': 'http://joe.blogspot.com',
          'wanted_games_qtd': 4,
          'birth_time': now()
        }
        self.person_recipe = Recipe(
          Person,
          **self.recipe_attrs
        )

    def test_flat_model_make_recipe_with_the_correct_attributes(self):
        """
          A 'flat model' means a model without associations, like
          foreign keys, many to many and one to one
        """
        person = self.person_recipe.make()
        self.assertEqual(person.name, self.recipe_attrs['name'])
        self.assertEqual(person.nickname, self.recipe_attrs['nickname'])
        self.assertEqual(person.age, self.recipe_attrs['age'])
        self.assertEqual(person.bio, self.recipe_attrs['bio'])
        self.assertEqual(person.birthday, self.recipe_attrs['birthday'])
        self.assertEqual(person.appointment, self.recipe_attrs['appointment'])
        self.assertEqual(person.blog, self.recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, self.recipe_attrs['wanted_games_qtd'])
        self.assertNotEqual(person.id, None)

    def test_flat_model_prepare_recipe_with_the_correct_attributes(self):
        person = self.person_recipe.prepare()
        self.assertEqual(person.name, self.recipe_attrs['name'])
        self.assertEqual(person.nickname, self.recipe_attrs['nickname'])
        self.assertEqual(person.age, self.recipe_attrs['age'])
        self.assertEqual(person.bio, self.recipe_attrs['bio'])
        self.assertEqual(person.birthday, self.recipe_attrs['birthday'])
        self.assertEqual(person.appointment, self.recipe_attrs['appointment'])
        self.assertEqual(person.blog, self.recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, self.recipe_attrs['wanted_games_qtd'])
        self.assertEqual(person.id, None)

    def test_accepts_callable(self):
        r = Recipe(DummyBlankFieldsModel,
            blank_char_field = lambda: 'callable!!'
        )
        value = r.make().blank_char_field
        self.assertEqual(value, 'callable!!')

    def test_always_calls_when_creating(self):
        with patch('test.generic.tests.test_recipes.choice') as choice_mock:
            l = ['foo', 'bar', 'spam', 'eggs']
            r = Recipe(DummyBlankFieldsModel,
                blank_char_field = lambda: choice(l)
            )
            r.make().blank_char_field
            r.make().blank_char_field
            self.assertEqual(choice_mock.call_count, 2)

    def test_always_calls_with_quantity(self):
        with patch('test.generic.tests.test_recipes.choice') as choice_mock:
            l = ['foo', 'bar', 'spam', 'eggs']
            r = Recipe(DummyBlankFieldsModel,
                blank_char_field = lambda: choice(l)
            )
            r.make(_quantity=3)
            self.assertEqual(choice_mock.call_count, 3)

    def test_make_recipes_with_args(self):
        """
          Overriding some fields values at recipe execution
        """
        person = self.person_recipe.make(name='Guido', age=56)
        self.assertNotEqual(person.name, self.recipe_attrs['name'])
        self.assertEqual(person.name, 'Guido')

        self.assertNotEqual(person.age, self.recipe_attrs['age'])
        self.assertEqual(person.age, 56)

        self.assertEqual(person.nickname, self.recipe_attrs['nickname'])
        self.assertEqual(person.bio, self.recipe_attrs['bio'])
        self.assertEqual(person.birthday, self.recipe_attrs['birthday'])
        self.assertEqual(person.appointment, self.recipe_attrs['appointment'])
        self.assertEqual(person.blog, self.recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, self.recipe_attrs['wanted_games_qtd'])
        self.assertNotEqual(person.id, None)

    def test_prepare_recipes_with_args(self):
        """
          Overriding some fields values at recipe execution
        """
        person = self.person_recipe.prepare(name='Guido', age=56)
        self.assertNotEqual(person.name, self.recipe_attrs['name'])
        self.assertEqual(person.name, 'Guido')

        self.assertNotEqual(person.age, self.recipe_attrs['age'])
        self.assertEqual(person.age, 56)

        self.assertEqual(person.nickname, self.recipe_attrs['nickname'])
        self.assertEqual(person.bio, self.recipe_attrs['bio'])
        self.assertEqual(person.birthday, self.recipe_attrs['birthday'])
        self.assertEqual(person.appointment, self.recipe_attrs['appointment'])
        self.assertEqual(person.blog, self.recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, self.recipe_attrs['wanted_games_qtd'])
        self.assertEqual(person.id, None)

    def test_make_recipe_without_all_model_needed_data(self):
        person_recipe = Recipe(Person, name='John Doe')
        person = person_recipe.make()
        self.assertEqual('John Doe', person.name)
        self.assertTrue(person.nickname)
        self.assertTrue(person.age)
        self.assertTrue(person.bio)
        self.assertTrue(person.birthday)
        self.assertTrue(person.appointment)
        self.assertTrue(person.blog)
        self.assertTrue(person.wanted_games_qtd)
        self.assertTrue(person.id)

    def test_prepare_recipe_without_all_model_needed_data(self):
        person_recipe = Recipe(Person, name='John Doe')
        person = person_recipe.prepare()
        self.assertEqual('John Doe', person.name)
        self.assertTrue(person.nickname)
        self.assertTrue(person.age)
        self.assertTrue(person.bio)
        self.assertTrue(person.birthday)
        self.assertTrue(person.appointment)
        self.assertTrue(person.blog)
        self.assertTrue(person.wanted_games_qtd)
        self.assertFalse(person.id)


class TestExecutingRecipes(TestCase):
    """
      Tests for calling recipes defined in mommy_recipes.py
    """
    def test_model_with_foreign_key(self):
        dog = mommy.make_recipe('test.generic.dog')
        self.assertEqual(dog.breed, 'Pug')
        self.assertIsInstance(dog.owner, Person)
        self.assertNotEqual(dog.owner.id, None)

        dog = mommy.prepare_recipe('test.generic.dog')
        self.assertEqual(dog.breed, 'Pug')
        self.assertIsInstance(dog.owner, Person)
        self.assertNotEqual(dog.owner.id, None)

    def test_model_with_foreign_key_as_str(self):
        dog = mommy.make_recipe('test.generic.other_dog')
        self.assertEqual(dog.breed, 'Basset')
        self.assertIsInstance(dog.owner, Person)
        self.assertNotEqual(dog.owner.id, None)

        dog = mommy.prepare_recipe('test.generic.other_dog')
        self.assertEqual(dog.breed, 'Basset')
        self.assertIsInstance(dog.owner, Person)
        self.assertNotEqual(dog.owner.id, None)

    def test_model_with_foreign_key_as_unicode(self):
        dog = mommy.make_recipe('test.generic.other_dog_unicode')
        self.assertEqual(dog.breed, 'Basset')
        self.assertIsInstance(dog.owner, Person)
        self.assertNotEqual(dog.owner.id, None)

        dog = mommy.prepare_recipe('test.generic.other_dog_unicode')
        self.assertEqual(dog.breed, 'Basset')
        self.assertIsInstance(dog.owner, Person)
        self.assertNotEqual(dog.owner.id, None)

    def test_make_recipe(self):
        person = mommy.make_recipe('test.generic.person')
        self.assertIsInstance(person, Person)
        self.assertNotEqual(person.id, None)

    def test_make_recipe_with_quantity_parameter(self):
        people = mommy.make_recipe('test.generic.person', _quantity=3)
        self.assertEqual(len(people), 3)
        for person in people:
            self.assertIsInstance(person, Person)
            self.assertNotEqual(person.id, None)

    def test_make_recipe_with_quantity_parameter_respection_model_args(self):
        people = mommy.make_recipe('test.generic.person', _quantity=3, name='Dennis Ritchie', age=70)
        self.assertEqual(len(people), 3)
        for person in people:
            self.assertEqual(person.name, 'Dennis Ritchie')
            self.assertEqual(person.age, 70)

    def test_make_recipe_raises_correct_exception_if_invalid_quantity(self):
        self.assertRaises(
            InvalidQuantityException,
            mommy.make_recipe, 'test.generic.person', _quantity="hi"
        )
        self.assertRaises(
            InvalidQuantityException,
            mommy.make_recipe, 'test.generic.person', _quantity=-1
        )

    def test_prepare_recipe_with_quantity_parameter(self):
        people = mommy.prepare_recipe('test.generic.person', _quantity=3)
        self.assertEqual(len(people), 3)
        for person in people:
            self.assertIsInstance(person, Person)
            self.assertEqual(person.id, None)

    def test_prepare_recipe_with_quantity_parameter_respection_model_args(self):
        people = mommy.prepare_recipe('test.generic.person', _quantity=3, name='Dennis Ritchie', age=70)
        self.assertEqual(len(people), 3)
        for person in people:
            self.assertEqual(person.name, 'Dennis Ritchie')
            self.assertEqual(person.age, 70)

    def test_prepare_recipe_raises_correct_exception_if_invalid_quantity(self):
        self.assertRaises(
            InvalidQuantityException,
            mommy.prepare_recipe, 'test.generic.person', _quantity="hi"
        )
        self.assertRaises(
            InvalidQuantityException,
            mommy.prepare_recipe, 'test.generic.person', _quantity=-1
        )

    def test_prepare_recipe(self):
        person = mommy.prepare_recipe('test.generic.person')
        self.assertIsInstance(person, Person)
        self.assertEqual(person.id, None)

    def test_make_recipe_with_args(self):
        person = mommy.make_recipe('test.generic.person', name='Dennis Ritchie', age=70)
        self.assertEqual(person.name, 'Dennis Ritchie')
        self.assertEqual(person.age, 70)

    def test_prepare_recipe_with_args(self):
        person = mommy.prepare_recipe('test.generic.person', name='Dennis Ritchie', age=70)
        self.assertEqual(person.name, 'Dennis Ritchie')
        self.assertEqual(person.age, 70)

    def test_import_recipe_inside_deeper_modules(self):
        recipe_name = 'test.generic.tests.sub_package.person'
        person = mommy.prepare_recipe(recipe_name)
        self.assertEqual(person.name, 'John Deeper')

    def test_make_many_from_recipe(self):
        """
        make_many_from_recipe is deprecated, so this test must be deleted when
        the method is
        """
        persons = mommy.make_many_from_recipe('test.generic.person')
        self.assertIsInstance(persons, list)
        self.assertEqual(len(persons), mommy.MAX_MANY_QUANTITY)
        for person in persons:
            self.assertIsInstance(person, Person)
            self.assertNotEqual(person.id, None)

    def test_make_many_from_recipe_with_specified_quantity(self):
        """
        make_many_from_recipe is deprecated, so this test must be deleted when
        the method is
        """
        quantity = 2
        persons = mommy.make_many_from_recipe('test.generic.person', quantity=quantity)
        self.assertIsInstance(persons, list)
        self.assertEqual(len(persons), quantity)

    def test_make_many_with_model_args(self):
        """
        make_many_from_recipe is deprecated, so this test must be deleted when
        the method is
        """
        persons = mommy.make_many_from_recipe('test.generic.person', name='Dennis Ritchie', age=70)
        for person in persons:
            self.assertEqual(person.name, 'Dennis Ritchie')
            self.assertEqual(person.age, 70)

class ForeignKeyTestCase(TestCase):
    def test_foreign_key_method_returns_a_recipe_foreign_key_object(self):
        number_recipe = Recipe(DummyNumbersModel,
            float_field = 1.6
        )
        obj = foreign_key(number_recipe)
        self.assertIsInstance(obj, RecipeForeignKey)

    def test_not_accept_other_type(self):
        with self.assertRaises(TypeError) as c:
            foreign_key(2)
        exception = c.exception
        self.assertEqual(str(exception), 'Not a recipe')

    def test_do_not_create_related_model(self):
        """
          It should not attempt to create other object when
          passing the object as argument
        """
        person = mommy.make_recipe('test.generic.person')
        self.assertEqual(Person.objects.count(), 1)
        mommy.make_recipe('test.generic.dog', owner=person)
        self.assertEqual(Person.objects.count(), 1)
        mommy.prepare_recipe('test.generic.dog', owner=person)
        self.assertEqual(Person.objects.count(), 1)

    def test_do_query_lookup_for_recipes_make_method(self):
        """
          It should not attempt to create other object when
          using query lookup syntax
        """
        dog = mommy.make_recipe('test.generic.dog', owner__name='James')
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(dog.owner.name, 'James')

    def test_do_query_lookup_for_recipes_prepare_method(self):
        """
          It should not attempt to create other object when
          using query lookup syntax
        """
        dog = mommy.prepare_recipe('test.generic.dog', owner__name='James')
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(dog.owner.name, 'James')

    def test_do_query_lookup_empty_recipes(self):
        """
          It should not attempt to create other object when
          using query lookup syntax
        """
        dog_recipe = Recipe(Dog)
        dog = dog_recipe.make(owner__name='James')
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(dog.owner.name, 'James')

        dog = dog_recipe.prepare(owner__name='Zezin')
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(dog.owner.name, 'Zezin')

    def test_related_models_recipes(self):
        lady = mommy.make_recipe('test.generic.dog_lady')
        self.assertEqual(lady.dog_set.count(), 2)
        self.assertEqual(lady.dog_set.all()[0].breed, 'Pug')
        self.assertEqual(lady.dog_set.all()[1].breed, 'Basset')

class TestSequences(TestCase):
    def test_increment_for_strings(self):
        person = mommy.make_recipe('test.generic.serial_person')
        self.assertEqual(person.name, 'joe1')
        person = mommy.prepare_recipe('test.generic.serial_person')
        self.assertEqual(person.name, 'joe2')
        person = mommy.make_recipe('test.generic.serial_person')
        self.assertEqual(person.name, 'joe3')

    def test_increment_for_numbers(self):
        dummy = mommy.make_recipe('test.generic.serial_numbers')
        self.assertEqual(dummy.default_int_field, 11)
        self.assertEqual(dummy.default_decimal_field, Decimal('21.1'))
        self.assertEqual(dummy.default_float_field, 2.23)
        dummy = mommy.make_recipe('test.generic.serial_numbers')
        self.assertEqual(dummy.default_int_field, 12)
        self.assertEqual(dummy.default_decimal_field, Decimal('22.1'))
        self.assertEqual(dummy.default_float_field, 3.23)
        dummy = mommy.prepare_recipe('test.generic.serial_numbers')
        self.assertEqual(dummy.default_int_field, 13)
        self.assertEqual(dummy.default_decimal_field, Decimal('23.1'))
        self.assertEqual(dummy.default_float_field, 4.23)

    def test_increment_for_numbers_2(self):
        """
        This test is a repeated one but it is necessary to ensure Sequences atomicity
        """
        dummy = mommy.make_recipe('test.generic.serial_numbers')
        self.assertEqual(dummy.default_int_field, 11)
        self.assertEqual(dummy.default_decimal_field, Decimal('21.1'))
        self.assertEqual(dummy.default_float_field, 2.23)
        dummy = mommy.make_recipe('test.generic.serial_numbers')
        self.assertEqual(dummy.default_int_field, 12)
        self.assertEqual(dummy.default_decimal_field, Decimal('22.1'))
        self.assertEqual(dummy.default_float_field, 3.23)
        dummy = mommy.prepare_recipe('test.generic.serial_numbers')
        self.assertEqual(dummy.default_int_field, 13)
        self.assertEqual(dummy.default_decimal_field, Decimal('23.1'))
        self.assertEqual(dummy.default_float_field, 4.23)

    def test_creates_unique_field_recipe_using_for_iterator(self):
        for i in range(1, 4):
            dummy = mommy.make_recipe('test.generic.dummy_unique_field')
            self.assertEqual(dummy.value, 10 + i)

    def test_creates_unique_field_recipe_using_quantity_argument(self):
        dummies= mommy.make_recipe('test.generic.dummy_unique_field', _quantity=3)
        self.assertEqual(11, dummies[0].value)
        self.assertEqual(12, dummies[1].value)
        self.assertEqual(13, dummies[2].value)

    def test_increment_by_3(self):
        dummy = mommy.make_recipe('test.generic.serial_numbers_by')
        self.assertEqual(dummy.default_int_field, 13)
        self.assertEqual(dummy.default_decimal_field, Decimal('22.5'))
        self.assertAlmostEqual(dummy.default_float_field, 3.030000)
        dummy = mommy.make_recipe('test.generic.serial_numbers_by')
        self.assertEqual(dummy.default_int_field, 16)
        self.assertEqual(dummy.default_decimal_field, Decimal('24.9'))
        self.assertAlmostEqual(dummy.default_float_field, 4.83)
        dummy = mommy.prepare_recipe('test.generic.serial_numbers_by')
        self.assertEqual(dummy.default_int_field, 19)
        self.assertEqual(dummy.default_decimal_field, Decimal('27.3'))
        self.assertAlmostEqual(dummy.default_float_field, 6.63)


class TestIterators(TestCase):

    def test_accepts_generators(self):
        r = Recipe(DummyBlankFieldsModel,
                   blank_char_field=itertools.cycle(['a', 'b']))
        self.assertEqual('a', r.make().blank_char_field)
        self.assertEqual('b', r.make().blank_char_field)
        self.assertEqual('a', r.make().blank_char_field)

    def test_accepts_iterators(self):
        r = Recipe(DummyBlankFieldsModel,
                   blank_char_field=iter(['a', 'b', 'c']))
        self.assertEqual('a', r.make().blank_char_field)
        self.assertEqual('b', r.make().blank_char_field)
        self.assertEqual('c', r.make().blank_char_field)

    def test_empty_iterator_exception(self):
        r = Recipe(DummyBlankFieldsModel,
                   blank_char_field=iter(['a', 'b']))
        self.assertEqual('a', r.make().blank_char_field)
        self.assertEqual('b', r.make().blank_char_field)
        self.assertRaises(RecipeIteratorEmpty, r.make)

    def test_only_iterators_not_iteratables_are_iterated(self):
        """Ensure we only iterate explicit iterators.

        Consider "iterable" vs "iterator":

        Something like a string is "iterable", but not an "iterator". We don't
        want to iterate "iterables", only explicit "iterators".

        """
        r = Recipe(DummyBlankFieldsModel,
                   blank_text_field="not an iterator, so don't iterate!")
        self.assertEqual(
            r.make().blank_text_field,
            "not an iterator, so don't iterate!")
