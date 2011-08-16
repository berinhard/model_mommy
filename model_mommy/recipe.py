#coding: utf-8

from model_mommy.mommy import Mommy
from model_mommy import mommy

class Recipe(object):
    def __init__(self, mommy_recipe_name, model, **attrs):
        self.name = mommy_recipe_name
        self.mommy_instance = Mommy(model)
        self.mommy_instance.attr_mapping = attrs
        if mommy.recipes is None:
            mommy.recipes = [self]
        else:
            mommy.recipes.append(self)

