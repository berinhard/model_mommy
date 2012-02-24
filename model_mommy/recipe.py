#coding: utf-8
import inspect

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def make(self):
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            if isinstance(v, Recipe):
                mapping[k] = v.make()
        return self.model.objects.create(**mapping)


def foreign_key(recipe_name):
    frame = inspect.stack()[1]
    mod = inspect.getmodule(frame[0])
    return getattr(mod, recipe_name)
