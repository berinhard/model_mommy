#coding: utf-8
import inspect
import mommy
from exceptions import RecipeNotFound

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def _mapping(self, new_attrs):
        fk_fields_attrs = dict((k, v) for k, v in new_attrs.items() if '__' in k)
        new_attrs = dict((k, v) for k, v in new_attrs.items() if not '__' in k)
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            # do not generate values if field value is provided
            if new_attrs.get(k):
                continue
            if callable(v):
                mapping[k] = v()
            elif isinstance(v, RecipeForeignKey):
                recipe_attrs = mommy.filter_fk_attrs(k, **fk_fields_attrs)
                mapping[k] = v.recipe.make(**recipe_attrs)
        mapping.update(new_attrs)
        return mapping

    def make(self, **attrs):
        return mommy.make(self.model, **self._mapping(attrs))

    def prepare(self, **attrs):
        return mommy.prepare_one(self.model, **self._mapping(attrs))


class RecipeForeignKey(object):

    def __init__(self, recipe):
        if isinstance(recipe, Recipe):
            self.recipe = recipe
        elif isinstance(recipe, str):
            frame = inspect.stack()[2]
            caller_module = inspect.getmodule(frame[0])
            recipe = getattr(caller_module, recipe)
            if recipe:
                self.recipe = recipe
            else:
                raise RecipeNotFound
        else:
            raise TypeError('Not a recipe')


def foreign_key(recipe):
    """
      Returns the callable, so that the associated model
      will not be created during the recipe definition.
    """
    return RecipeForeignKey(recipe)
