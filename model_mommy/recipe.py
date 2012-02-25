#coding: utf-8

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def _mapping(self):
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            if callable(v):
                mapping[k] = v()
        return mapping

    def make(self):
        return self.model.objects.create(**self._mapping())

    def prepare(self):
        return self.model(**self._mapping())


def foreign_key(recipe):
    """
      Returns the callable, so that the associated model
      will not be created during the recipe definition.
    """
    if isinstance(recipe, Recipe):
        return recipe.make
    else:
        raise TypeError('Not a recipe')

