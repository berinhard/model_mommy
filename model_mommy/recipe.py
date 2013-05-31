#coding: utf-8
import inspect
import mommy
from exceptions import RecipeNotFound

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def _mapping(self, new_attrs):
        rel_fields_attrs = dict((k, v) for k, v in new_attrs.items() if '__' in k)
        new_attrs = dict((k, v) for k, v in new_attrs.items() if not '__' in k)
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            # do not generate values if field value is provided
            if new_attrs.get(k):
                continue
            if callable(v):
                mapping[k] = v()
            elif isinstance(v, RecipeForeignKey):
                recipe_attrs = mommy.filter_rel_attrs(k, **rel_fields_attrs)
                mapping[k] = v.recipe.make(**recipe_attrs)
        mapping.update(new_attrs)
        return mapping

    def make(self, **attrs):
        return mommy.make(self.model, **self._mapping(attrs))

    def prepare(self, **attrs):
        return mommy.prepare(self.model, **self._mapping(attrs))


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

def seq(value, increment_by=1):
    return Sequence(value, increment_by=increment_by)

class Sequence(object):

    def __init__(self, value, increment_by=1):
        self.value = value
        self.counter = 1
        self.increment_by = increment_by

    def get_inc(self, model):
        if not model.objects.count():
            self.counter = self.increment_by
        i = self.counter
        self.counter += self.increment_by
        return i

    def gen(self, model):
        inc = self.get_inc(model)
        return self.value + type(self.value)(inc)


