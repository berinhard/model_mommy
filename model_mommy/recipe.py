#coding: utf-8

from model_mommy.mommy import Mommy

class Recipe(object):
    def __init__(self, mommy_recipe_name, model, **attrs):
        self.name = mommy_recipe_name
        self.mommy_instance = Mommy(model)
        self.mommy_instance.attr_mapping = attrs
