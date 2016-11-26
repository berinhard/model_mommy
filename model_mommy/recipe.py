#coding: utf-8
from functools import wraps
import inspect
import itertools
from . import mommy
from .timezone import tz_aware
from .exceptions import RecipeNotFound, RecipeIteratorEmpty

from six import string_types
import datetime


# Python 2.6.x compatibility code
itertools_count = itertools.count
try:
    itertools_count(0, 1)
except TypeError:
    def count(start=0, step=1):
        n = start
        while True:
            yield n
            n += step
    itertools_count =  count

finder = mommy.ModelFinder()

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model
        # _iterator_backups will hold values of the form (backup_iterator, usable_iterator).
        self._iterator_backups = {}

    def _mapping(self, new_attrs):
        _save_related = new_attrs.get('_save_related', True)
        rel_fields_attrs = dict((k, v) for k, v in new_attrs.items() if '__' in k)
        new_attrs = dict((k, v) for k, v in new_attrs.items() if not '__' in k)
        mapping = self.attr_mapping.copy()
        for k, v in self.attr_mapping.items():
            # do not generate values if field value is provided
            if new_attrs.get(k):
                continue
            elif mommy.is_iterator(v):
                if isinstance(self.model, string_types):
                    m = finder.get_model(self.model)
                else:
                    m = self.model
                if m.objects.count() == 0 or k not in self._iterator_backups:
                    self._iterator_backups[k] = itertools.tee(self._iterator_backups.get(k, [v])[0])
                mapping[k] = self._iterator_backups[k][1]
            elif isinstance(v, RecipeForeignKey):
                a={}
                for key, value in list(rel_fields_attrs.items()):
                    if key.startswith('%s__' % k):
                        a[key] = rel_fields_attrs.pop(key)
                recipe_attrs = mommy.filter_rel_attrs(k, **a)
                if _save_related:
                    mapping[k] = v.recipe.make(**recipe_attrs)
                else:
                    mapping[k] = v.recipe.prepare(**recipe_attrs)
            elif isinstance(v, related):
                mapping[k] = v.make()
        mapping.update(new_attrs)
        mapping.update(rel_fields_attrs)
        return mapping

    def make(self, **attrs):
        return mommy.make(self.model, **self._mapping(attrs))

    def prepare(self, **attrs):
        defaults = {'_save_related': False}
        defaults.update(attrs)
        return mommy.prepare(self.model, **self._mapping(defaults))

    def extend(self, **attrs):
        attr_mapping = self.attr_mapping.copy()
        attr_mapping.update(attrs)
        return Recipe(self.model, **attr_mapping)


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


def _total_secs(td):
    """
    python 2.6 compatible timedelta total seconds calculation
    backport from
    https://docs.python.org/2.7/library/datetime.html#datetime.timedelta.total_seconds
    """
    if hasattr(td, 'total_seconds'):
        return td.total_seconds()
    else:
        #py26
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.0**6


def seq(value, increment_by=1):
    if type(value) in [datetime.datetime, datetime.date,  datetime.time]:
        if type(value) is datetime.date:
            date = datetime.datetime.combine(value, datetime.datetime.now().time())
        elif type(value) is datetime.time:
            date = datetime.datetime.combine(datetime.date.today(), value)
        else:
            date = value
        # convert to epoch time
        start = _total_secs((date - datetime.datetime(1970, 1, 1)))
        increment_by = _total_secs(increment_by)
        for n in itertools_count(increment_by, increment_by):
            series_date = tz_aware(datetime.datetime.utcfromtimestamp(start + n))
            if type(value) is datetime.time:
                yield series_date.time()
            elif type(value) is datetime.date:
                yield series_date.date()
            else:
                yield series_date
    else:
        for n in itertools_count(increment_by, increment_by):
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

    def make(self):
        """
         Persists objects to m2m relation
        """
        return [m.make() for m in self.related]
