#coding: utf-8
import inspect
import mommy


class RecipeNotFound(Exception):
    pass

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def _mapping(self, new_attrs):
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            if callable(v):
                mapping[k] = v()
        mapping.update(new_attrs)
        return mapping

    def make(self, **attrs):
        return mommy.make_one(self.model, **self._mapping(attrs))

    def prepare(self, **attrs):
        return self.model(**self._mapping(attrs))


def foreign_key(recipe):
    """
      Returns the callable, so that the associated model
      will not be created during the recipe definition.
    """
    if isinstance(recipe, Recipe):
        return recipe.make
    elif isinstance(recipe, str):
        frame = inspect.stack()[1]
        caller_module = inspect.getmodule(frame[0])
        recipe = getattr(caller_module, recipe)
        if recipe:
            return recipe.make
        else:
            raise RecipeNotFound
    else:
        raise TypeError('Not a recipe')
