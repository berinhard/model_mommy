#coding: utf-8

from django.test import TestCase
from model_mommy import mommy
from model_mommy.models import Person
from model_mommy.recipe import Recipe
from datetime import date

class TestDefiningRecipes(TestCase):
    def tearDown(self):
        mommy.recipes = []

    def test_flat_model_recipe_definition(self):
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
        recipe = Recipe(
          'person',
          'model_mommy.Person',
          **recipe_attrs
        )
        self.assertEqual(mommy.recipes, [recipe])

    def test_flat_model_make_recipe_with_the_correct_attributes(self):
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
        recipe = Recipe(
          'joe person',
          'model_mommy.Person',
          **recipe_attrs
        )
        person = mommy.make_recipe('joe person')
        self.assertEqual(person.name, recipe_attrs['name'])
        self.assertEqual(person.nickname, recipe_attrs['nickname'])
        self.assertEqual(person.age, recipe_attrs['age'])
        self.assertEqual(person.bio, recipe_attrs['bio'])
        self.assertEqual(person.birthday, recipe_attrs['birthday'])
        self.assertEqual(person.appointment, recipe_attrs['appointment'])
        self.assertEqual(person.blog, recipe_attrs['blog'])
        self.assertEqual(person.wanted_games_qtd, recipe_attrs['wanted_games_qtd'])
