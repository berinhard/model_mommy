#coding: utf-8
import inspect
import itertools
from . import mommy
from .exceptions import RecipeNotFound, RecipeIteratorEmpty

from six import string_types


class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model
        # _iterator_backups will hold values of the form (backup_iterator, usable_iterator).
        self._iterator_backups = {}

    def _mapping(self, new_attrs):
        rel_fields_attrs = dict((k, v) for k, v in new_attrs.items() if '__' in k)
        new_attrs = dict((k, v) for k, v in new_attrs.items() if not '__' in k)
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            # do not generate values if field value is provided
            if new_attrs.get(k):
                continue
            elif mommy.is_iterator(v):
                if self.model.objects.count() == 0:
                    self._iterator_backups[k] = itertools.tee(self._iterator_backups.get(k, [v])[0])
                mapping[k] = self._iterator_backups[k][1]
            elif isinstance(v, RecipeForeignKey):
                a={}
                for key, value in list(rel_fields_attrs.items()):
                    if key.startswith('%s__' % k):
                        a[key] = rel_fields_attrs.pop(key)
                recipe_attrs = mommy.filter_rel_attrs(k, **a)
                mapping[k] = v.recipe.make(**recipe_attrs)
            elif isinstance(v, related):
                mapping[k] = v.prepare()
        mapping.update(new_attrs)
        mapping.update(rel_fields_attrs)
        return mapping

    def make(self, **attrs):
        return mommy.make(self.model, **self._mapping(attrs))

    def prepare(self, **attrs):
        return mommy.prepare(self.model, **self._mapping(attrs))


class RecipeForeignKey(object):

    def __init__(self, recipe):
        if isinstance(recipe, Recipe):
            self.recipe = recipe
        elif isinstance(recipe, string_types):
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
    for n in itertools.count(increment_by, increment_by):
        yield value + type(value)(n)

class related(object):
    def __init__(self, *args):
        self.related = []
        for recipe in args:
            if isinstance(recipe, Recipe):
                self.related.append(recipe)
            elif isinstance(recipe, string_types):
                frame = inspect.stack()[1]
                caller_module = inspect.getmodule(frame[0])
                recipe = getattr(caller_module, recipe)
                if recipe:
                    self.related.append(recipe)
                else:
                    raise RecipeNotFound
            else:
                raise TypeError('Not a recipe')

    def prepare(self):
        """
            Django related manager saves related set.
            No need to persist at first
        """
        return [m.prepare() for m in self.related]

