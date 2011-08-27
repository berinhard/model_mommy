#coding: utf-8

from model_mommy.mommy import Mommy
from model_mommy import mommy

from django.db.models import get_model

def _find_model(model):
    if isinstance(model, str):
        app_label, model_name = model.split('.')
        model = get_model(app_label, model_name)
        if not model:
            raise ModelNotFound("could not find model '%s' in the app '%s'." %(model_name, app_label))
    return model

class Recipe(object):
    def __init__(self, mommy_recipe_name, model, **attrs):
        self.name = mommy_recipe_name
        self.attr_mapping = attrs
        self.model = _find_model(model)
        if mommy.recipes is None:
            mommy.recipes = [self]
        else:
            mommy.recipes.append(self)

    def make(self):
        return self.model.objects.create(**self.attr_mapping)
