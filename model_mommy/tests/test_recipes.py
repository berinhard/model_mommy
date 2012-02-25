#coding: utf-8

from django.test import TestCase
from model_mommy import mommy
from model_mommy.models import Person, DummyNumbersModel, DummyBlankFieldsModel
from model_mommy.recipe import Recipe, foreign_key
from datetime import date

class TestDefiningRecipes(TestCase):

    def test_flat_model_make_recipe_with_the_correct_attributes(self):
        """
          A 'flat model' means a model without associations, like
          foreign keys, many to many and one to one
        """
        recipe_attrs = {
          'name': 'John Doe',
          'nickname': 'joe',
          'age': 18,
          'bio': 'Someone in the crowd',
          'birthday': date.today(),
          'appointment': date.today(),
          'blog': 'http://joe.blogspot.com',
          'wanted_games_qtd': 4,
        }
        person_recipe = Recipe(
          Person,
          **recipe_attrs
        )
        person = person_recipe.make()
        self.assertEqual(person.name, recipe_attrs['name'])
        self.assertEqual(person.nickname, recipe_attrs['nickname'])
        self.assertEqual(person.age, recipe_attrs['age'])
        self.assertEqual(person.bio, recipe_attrs['bio'])
        self.assertEqual(person.birthday, recipe_attrs['birthday'])
        self.assertEqual(person.appointment, recipe_attrs['appointment'])
        self.assertEqual(person.blog, recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, recipe_attrs['wanted_games_qtd'])
        self.assertNotEqual(person.id, None)

    def test_flat_model_prepare_recipe_with_the_correct_attributes(self):
        recipe_attrs = {
          'name': 'John Doe',
          'nickname': 'joe',
          'age': 18,
          'bio': 'Someone in the crowd',
          'birthday': date.today(),
          'appointment': date.today(),
          'blog': 'http://joe.blogspot.com',
          'wanted_games_qtd': 4,
        }
        person_recipe = Recipe(
          Person,
          **recipe_attrs
        )
        person = person_recipe.prepare()
        self.assertEqual(person.name, recipe_attrs['name'])
        self.assertEqual(person.nickname, recipe_attrs['nickname'])
        self.assertEqual(person.age, recipe_attrs['age'])
        self.assertEqual(person.bio, recipe_attrs['bio'])
        self.assertEqual(person.birthday, recipe_attrs['birthday'])
        self.assertEqual(person.appointment, recipe_attrs['appointment'])
        self.assertEqual(person.blog, recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, recipe_attrs['wanted_games_qtd'])
        self.assertEqual(person.id, None)

    def test_model_with_foreign_key(self):
        dog = mommy.make_recipe('model_mommy.dog')
        self.assertEqual(dog.breed, 'Pug')
        self.assertTrue(isinstance(dog.owner, Person))

    def test_make_recipe(self):
        person = mommy.make_recipe('model_mommy.person')
        self.assertTrue(isinstance(person, Person))
        self.assertNotEqual(person.id, None)

    def test_make_recipe(self):
        person = mommy.prepare_recipe('model_mommy.person')
        self.assertTrue(isinstance(person, Person))
        self.assertEqual(person.id, None)

    def test_accepts_callable(self):
        r = Recipe(DummyBlankFieldsModel,
            blank_char_field = lambda: 'callable!!'
        )
        value = r.make().blank_char_field
        self.assertEqual(value, 'callable!!')

class ForeignKeyTestCase(TestCase):
    def test_returns_a_callable(self):
        number_recipe = Recipe(DummyNumbersModel,
            float_field = 1.6
        )
        method = foreign_key(number_recipe)
        self.assertTrue(callable(method))
        self.assertTrue(method.im_self, number_recipe)

    def test_not_accept_other_type(self):
        with self.assertRaises(TypeError) as c:
            foreign_key('something')
        exception = c.exception
        self.assertEqual(exception.message, 'Not a recipe')
