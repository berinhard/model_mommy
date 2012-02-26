#coding: utf-8

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
        return self.model.objects.create(**self._mapping(attrs))

    def prepare(self, **attrs):
        return self.model(**self._mapping(attrs))


def foreign_key(recipe):
    """
      Returns the callable, so that the associated model
      will not be created during the recipe definition.
    """
    if isinstance(recipe, Recipe):
        return recipe.make
    else:
        raise TypeError('Not a recipe')

