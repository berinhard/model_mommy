#coding: utf-8

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def make(self):
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            if callable(v):
                mapping[k] = v()
        return self.model.objects.create(**mapping)


def foreign_key(recipe):
    """
      Returns the callable, so that the associated model
      will not be created during the recipe definition.
    """
    if isinstance(recipe, Recipe):
        return recipe.make
    else:
        raise TypeError('Not a recipe')

