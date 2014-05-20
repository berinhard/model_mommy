# -*- coding: utf-8 -*-
import warnings

from django.conf import settings
from django.utils import importlib
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import django
from django.db.models.loading import get_model
if django.VERSION >= (1, 7):
    from django.apps import apps
else:
    from django.db.models.loading import cache
from django.db.models.base import ModelBase
from django.db.models import (
    CharField, EmailField, SlugField, TextField, URLField,
    DateField, DateTimeField, TimeField,
    AutoField, IntegerField, SmallIntegerField,
    PositiveIntegerField, PositiveSmallIntegerField,
    BooleanField, DecimalField, FloatField,
    FileField, ImageField, Field,
    ForeignKey, ManyToManyField, OneToOneField)
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor
try:
    from django.db.models import BigIntegerField
except ImportError:
    BigIntegerField = IntegerField

from . import generators
from .exceptions import ModelNotFound, AmbiguousModelName, InvalidQuantityException, RecipeIteratorEmpty

from six import string_types, advance_iterator, PY3

recipes = None

# FIXME: use pkg_resource
from os.path import dirname, join
mock_file_jpeg = join(dirname(__file__), 'mock-img.jpeg')
mock_file_txt = join(dirname(__file__), 'mock_file.txt')


#TODO: improve related models handling
foreign_key_required = [lambda field: ('model', field.related.parent_model)]

MAX_MANY_QUANTITY = 5

def make(model, _quantity=None, make_m2m=False, **attrs):
    """
    Creates a persisted instance from a given model its associated models.
    It fill the fields with random values or you can specify
    which fields you want to define its values by yourself.
    """
    mommy = Mommy(model, make_m2m=make_m2m)
    if _quantity and (not isinstance(_quantity, int) or _quantity < 1):
        raise InvalidQuantityException

    if _quantity:
        return [mommy.make(**attrs) for i in range(_quantity)]
    else:
        return mommy.make(**attrs)


def prepare(model, _quantity=None, **attrs):
    """
    Creates a BUT DOESN'T persist an instance from a given model its
    associated models.
    It fill the fields with random values or you can specify
    which fields you want to define its values by yourself.
    """
    mommy = Mommy(model)
    if _quantity and (not isinstance(_quantity, int) or _quantity < 1):
        raise InvalidQuantityException

    if _quantity:
        return [mommy.prepare(**attrs) for i in range(_quantity)]
    else:
        return mommy.prepare(**attrs)


def _recipe(name):
    app, recipe_name = name.rsplit('.', 1)
    recipes = importlib.import_module('.'.join([app, 'mommy_recipes']))
    return getattr(recipes, recipe_name)

def make_recipe(mommy_recipe_name, _quantity=None, **new_attrs):
    return _recipe(mommy_recipe_name).make(_quantity=_quantity, **new_attrs)

def prepare_recipe(mommy_recipe_name, _quantity=None, **new_attrs):
    return _recipe(mommy_recipe_name).prepare(_quantity=_quantity, **new_attrs)


def __m2m_generator(model, **attrs):
    return make(model, _quantity=MAX_MANY_QUANTITY, **attrs)

make.required = foreign_key_required
prepare.required = foreign_key_required
__m2m_generator.required = foreign_key_required

default_mapping = {
    BooleanField: generators.gen_boolean,
    IntegerField: generators.gen_integer,
    BigIntegerField: generators.gen_integer,
    SmallIntegerField: generators.gen_integer,

    PositiveIntegerField: lambda: generators.gen_integer(0),
    PositiveSmallIntegerField: lambda: generators.gen_integer(0),

    FloatField: generators.gen_float,
    DecimalField: generators.gen_decimal,

    CharField: generators.gen_string,
    TextField: generators.gen_text,
    SlugField: generators.gen_slug,

    ForeignKey: make,
    OneToOneField: make,
    ManyToManyField: __m2m_generator,

    DateField: generators.gen_date,
    DateTimeField: generators.gen_datetime,
    TimeField: generators.gen_time,

    URLField: generators.gen_url,
    EmailField: generators.gen_email,
    FileField: generators.gen_file_field,
    ImageField: generators.gen_image_field,

    ContentType: generators.gen_content_type,
}


class ModelFinder(object):
    '''
    Encapsulates all the logic for finding a model to Mommy.
    '''
    _unique_models = None
    _ambiguous_models = None

    def get_model(self, name):
        '''
        Get a model.

        :param name String on the form 'applabel.modelname' or 'modelname'.
        :return a model class.
        '''
        try:
            if '.' in name:
                app_label, model_name = name.split('.')
                model = get_model(app_label, model_name)
            else:
                model = self.get_model_by_name(name)
        except LookupError:  # Django 1.7.0a1 throws an exception
            # Lower djangos just fail silently
            model = None

        if not model:
            raise ModelNotFound("Could not find model '%s'." % name.title())

        return model

    def get_model_by_name(self, name):
        '''
        Get a model by name.

        If a model with that name exists in more than one app,
        raises AmbiguousModelName.
        '''
        name = name.lower()

        if self._unique_models is None:
            self._populate()

        if name in self._ambiguous_models:
            raise AmbiguousModelName('%s is a model in more than one app. '
                                     'Use the form "app.model".' % name.title())

        return self._unique_models.get(name)

    def _populate(self):
        '''
        Cache models for faster self._get_model.
        '''
        unique_models = {}
        ambiguous_models = []

        if django.VERSION >= (1, 7):
            all_models = apps.all_models
        else:
            all_models = cache.app_models

        for app_model in all_models.values():
            for name, model in app_model.items():
                if name not in unique_models:
                    unique_models[name] = model
                else:
                    ambiguous_models.append(name)

        for name in ambiguous_models:
            unique_models.pop(name, None)

        self._ambiguous_models = ambiguous_models
        self._unique_models = unique_models


def is_iterator(value):
    if PY3:
        return hasattr(value, '__next__')
    else:
        return hasattr(value, 'next')


class Mommy(object):
    attr_mapping = {}
    type_mapping = None

    # Note: we're using one finder for all Mommy instances to avoid
    # rebuilding the model cache for every make_* or prepare_* call.
    finder = ModelFinder()

    def __init__(self, model, make_m2m=False):
        self.make_m2m = make_m2m
        self.m2m_dict = {}

        if isinstance(model, ModelBase):
            self.model = model
        else:
            self.model = self.finder.get_model(model)

        self.init_type_mapping()

    def init_type_mapping(self):
        self.type_mapping = default_mapping.copy()
        generator_from_settings = getattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', {})
        for k, v in generator_from_settings.items():
            path, field_name = k.rsplit('.', 1)
            field_class = getattr(importlib.import_module(path), field_name)
            self.type_mapping[field_class] = v

    def make(self, **attrs):
        '''Creates and persists an instance of the model
        associated with Mommy instance.'''
        return self._make(commit=True, **attrs)

    def prepare(self, **attrs):
        '''Creates, but do not persists, an instance of the model
        associated with Mommy instance.'''
        self.type_mapping[ForeignKey] = prepare
        self.type_mapping[OneToOneField] = prepare
        return self._make(commit=False, **attrs)

    def get_fields(self):
        return self.model._meta.fields + self.model._meta.many_to_many

    def _make(self, commit=True, **attrs):
        is_rel_field = lambda x: '__' in x
        iterator_attrs = dict((k, v) for k, v in attrs.items() if is_iterator(v))
        model_attrs = dict((k, v) for k, v in attrs.items() if not is_rel_field(k))
        self.rel_attrs = dict((k, v) for k, v in attrs.items() if is_rel_field(k))
        self.rel_fields = [x.split('__')[0] for x in self.rel_attrs.keys() if is_rel_field(x)]

        for field in self.get_fields():

            # Skip links to parent so parent is not created twice.
            if isinstance(field, OneToOneField) and field.rel.parent_link:
                continue

            field_value_not_defined = field.name not in model_attrs

            if isinstance(field, (AutoField, generic.GenericRelation)):
                continue

            if all([field.name not in model_attrs, field.name not in self.rel_fields, field.name not in self.attr_mapping]):
                # Django is quirky in that BooleanFields are always "blank", but have no default default.
                if not issubclass(field.__class__, Field) or field.has_default() or (field.blank and not isinstance(field, BooleanField)):
                    continue

            if isinstance(field, ManyToManyField):
                if field.name not in model_attrs:
                    self.m2m_dict[field.name] = self.m2m_value(field)
                else:
                    self.m2m_dict[field.name] = model_attrs.pop(field.name)
            elif field_value_not_defined:
                if field.name not in self.rel_fields and field.null:
                    continue
                else:
                    model_attrs[field.name] = self.generate_value(field)
            elif callable(model_attrs[field.name]):
                model_attrs[field.name] = model_attrs[field.name]()
            elif field.name in iterator_attrs:
                try:
                    model_attrs[field.name] = advance_iterator(iterator_attrs[field.name])
                except StopIteration:
                    raise RecipeIteratorEmpty('{} iterator is empty.'.format(field.name))

        return self.instance(model_attrs, _commit=commit)

    def m2m_value(self, field):
        if field.name in self.rel_fields:
            return self.generate_value(field)
        if not self.make_m2m or field.null:
            return []
        return self.generate_value(field)

    def instance(self, attrs, _commit):
        one_to_many_keys = {}
        for k in tuple(attrs.keys()):
            field = getattr(self.model, k, None)
            if isinstance(field, ForeignRelatedObjectsDescriptor):
                one_to_many_keys[k] = attrs.pop(k)
        instance = self.model(**attrs)
        # m2m only works for persisted instances
        if _commit:
            instance.save()
            self._handle_one_to_many(instance, one_to_many_keys)
            self._handle_m2m(instance)
        return instance

    def _handle_one_to_many(self, instance, attrs):
        for k, v in attrs.items():
            setattr(instance, k, v)

    def _handle_m2m(self, instance):
        for key, values in self.m2m_dict.items():
            if not values:
                continue

            m2m_relation = getattr(instance, key)
            through_model = m2m_relation.through
            through_fields = through_model._meta.fields

            instance_key, value_key = '', ''
            for field in through_fields:
                if isinstance(field, ForeignKey):
                    if isinstance(instance, field.rel.to):
                        instance_key = field.name
                    elif isinstance(values[0], field.rel.to):
                        value_key = field.name

            base_kwargs = {instance_key: instance}
            for model_instance in values:
                base_kwargs[value_key] = model_instance
                make(through_model, **base_kwargs)

    def generate_value(self, field):
        '''
        Calls the generator associated with a field passing all required args.

        Generator Resolution Precedence Order:
        -- attr_mapping - mapping per attribute name
        -- choices -- mapping from avaiable field choices
        -- type_mapping - mapping from user defined type associated generators
        -- default_mapping - mapping from pre-defined type associated
           generators

        `attr_mapping` and `type_mapping` can be defined easely overwriting the
        model.
        '''
        if field.name in self.attr_mapping:
            generator = self.attr_mapping[field.name]
        elif getattr(field, 'choices'):
            generator = generators.gen_from_choices(field.choices)
        elif isinstance(field, ForeignKey) and isinstance(field.rel.to, ContentType):
            generator = self.type_mapping[ContentType]
        elif field.__class__ in self.type_mapping:
            generator = self.type_mapping[field.__class__]
        else:
            raise TypeError('%s is not supported by mommy.' % field.__class__)

        # attributes like max_length, decimal_places are take in account when
        # generating the value.
        generator_attrs = get_required_values(generator, field)

        if field.name in self.rel_fields:
            generator_attrs.update(filter_rel_attrs(field.name, **self.rel_attrs))

        return generator(**generator_attrs)


def get_required_values(generator, field):
    '''
    Gets required values for a generator from the field.
    If required value is a function, call's it with field as argument.
    If required value is a string, simply fetch the value from the field
    and returns.
    '''
    #FIXME: avoid abreviations
    rt = {}
    if hasattr(generator, 'required'):
        for item in generator.required:

            if callable(item):  # mommy can deal with the nasty hacking too!
                key, value = item(field)
                rt[key] = value

            elif isinstance(item, string_types):
                rt[item] = getattr(field, item)

            else:
                raise ValueError("Required value '%s' is of wrong type. \
                                  Don't make mommy sad." % str(item))

    return rt

def filter_rel_attrs(field_name, **rel_attrs):
    clean_dict = {}

    for k, v in rel_attrs.items():
        if k.startswith(field_name + '__'):
            splited_key = k.split('__')
            key = '__'.join(splited_key[1:])
            clean_dict[key] = v
        else:
            clean_dict[k] = v

    return clean_dict


### DEPRECATED METHODS (should be removed on the future)
def make_many(model, quantity=None, **attrs):
    msg = "make_many is deprecated. You should use make with _quantity parameter."
    warnings.warn(msg, DeprecationWarning)
    quantity = quantity or MAX_MANY_QUANTITY
    mommy = Mommy(model)
    return [mommy.make(**attrs) for i in range(quantity)]


def make_one(model, make_m2m=False, **attrs):
    msg = "make_one is deprecated. You should use the method make instead."
    warnings.warn(msg, DeprecationWarning)
    mommy = Mommy(model, make_m2m=make_m2m)
    return mommy.make(**attrs)


def prepare_one(model, **attrs):
    msg = "prepare_one is deprecated. You should use the method prepare instead."
    warnings.warn(msg, DeprecationWarning)
    mommy = Mommy(model)
    return mommy.prepare(**attrs)


def make_many_from_recipe(mommy_recipe_name, quantity=None, **new_attrs):
    msg = "make_many_from_recipe is deprecated. You should use the method make_recipe with the _quantity parameter instead."
    warnings.warn(msg, DeprecationWarning)
    quantity = quantity or MAX_MANY_QUANTITY
    return [make_recipe(mommy_recipe_name, **new_attrs) for x in range(quantity)]
