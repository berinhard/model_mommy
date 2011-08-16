#coding: utf-8

from django.test import TestCase
from model_mommy import mommy
from model_mommy.models import Person
from model_mommy.recipe import Recipe
from datetime import date

class TestDefiningRecipes(TestCase):

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
    self.assertTrue(isinstance(recipe.mommy_instance, mommy.Mommy))
    self.assertEqual(recipe.name, 'person')
    self.assertEqual(recipe.mommy_instance.attr_mapping, recipe_attrs)
