# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import importlib

from django.db.models.fields import AutoField, CharField, TextField, SlugField
from django.db.models.fields import DateField, DateTimeField, TimeField, EmailField
from django.db.models.fields import IntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField
from django.db.models.fields import BooleanField
from django.db.models.fields import URLField
from django.db.models  import FileField
from django.db.models import get_model

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.db.models import ForeignKey, ManyToManyField

try:
    from django.db.models.fields import BigIntegerField
except ImportError:
    BigIntegerField = IntegerField

import generators

recipes = None

#TODO: improve related models handling
foreign_key_required = [lambda field: ('model', field.related.parent_model)]

MAX_SELF_REFERENCE_LOOPS = 2
MAX_MANY_QUANTITY = 5

def make_one(model, **attrs):
    """
    Creates a persisted instance from a given model its associated models.
    It fill the fields with random values or you can specify
    which fields you want to define its values by yourself.
    """
    mommy = Mommy(model)
    return mommy.make_one(**attrs)


def prepare_one(model, **attrs):
    """
    Creates a BUT DOESN'T persist an instance from a given model its
    associated models.
    It fill the fields with random values or you can specify
    which fields you want to define its values by yourself.
    """
    mommy = Mommy(model)
    return mommy.prepare(**attrs)


def make_many(model, quantity=None, **attrs):
    quantity = quantity or MAX_MANY_QUANTITY
    mommy = Mommy(model)
    return [mommy.make_one(**attrs) for i in range(quantity)]

def _recipe(name):
    app, recipe_name = name.split('.')
    recipes = importlib.import_module('.'.join([app, 'mommy_recipes']))
    return getattr(recipes, recipe_name)

def make_recipe(mommy_recipe_name, **new_attrs):
    return _recipe(mommy_recipe_name).make(**new_attrs)

def prepare_recipe(mommy_recipe_name, **new_attrs):
    return _recipe(mommy_recipe_name).prepare(**new_attrs)

make_one.required = foreign_key_required
prepare_one.required = foreign_key_required
make_many.required = foreign_key_required

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

    ForeignKey: make_one,
    #OneToOneField: make_one,
    ManyToManyField: make_many,

    DateField: generators.gen_date,
    DateTimeField: generators.gen_datetime,
    TimeField: generators.gen_time,

    URLField: generators.gen_url,
    EmailField: generators.gen_email,
    FileField: generators.gen_file_field,

    ContentType: generators.gen_content_type,
}

class ModelNotFound(Exception):
    pass

class Mommy(object):
    attr_mapping = {}
    type_mapping = None

    def __init__(self, model):
        self.type_mapping = default_mapping.copy()
        if isinstance(model, str):
            app_label, model_name = model.split('.')
            self.model = get_model(app_label, model_name)
            if not self.model:
                raise ModelNotFound("could not find model '%s' in the app '%s'." %(model_name, app_label))
        else:
            self.model = model

    def make_one(self, **attrs):
        '''Creates and persists an instance of the model
        associated with Mommy instance.'''

        return self._make_one(commit=True, **attrs)

    def prepare(self, **attrs):
        '''Creates, but do not persists, an instance of the model
        associated with Mommy instance.'''
        self.type_mapping[ForeignKey] = prepare_one
        return self._make_one(commit=False, **attrs)

    def get_fields(self):
        return self.model._meta.fields + self.model._meta.many_to_many

    #Method too big
    def _make_one(self, commit=True, **attrs):
        m2m_dict = {}

        for field in self.get_fields():
            field_value_not_defined = field.name not in attrs

            if isinstance(field, (AutoField, generic.GenericRelation)):
                continue

            # If not specified, django automatically sets blank=True and
            # default on BooleanFields so we don't need to check these
            if not isinstance(field, BooleanField):
                if field.has_default() or field.blank:
                    continue

            if isinstance(field, ManyToManyField):
                if field_value_not_defined:
                    if field.null:
                        continue
                    else:
                        m2m_dict[field.name] = self.generate_value(field)
                else:
                    m2m_dict[field.name] = attrs.pop(field.name)

            elif field_value_not_defined:
                if field.null:
                    continue
                else:
                    attrs[field.name] = self.generate_value(field)

        instance = self.model(**attrs)

        # m2m only works for persisted instances
        if commit:
            instance.save()

            # m2m relation is treated differently
            for key, value in m2m_dict.items():
                m2m_relation = getattr(instance, key)
                for model_instance in value:
                    m2m_relation.add(model_instance)

        return instance

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
        elif isinstance(field, ForeignKey) and field.rel.to is ContentType:
            generator = self.type_mapping[ContentType]
        elif field.__class__ in self.type_mapping:
            generator = self.type_mapping[field.__class__]
        else:
            raise TypeError('%s is not supported by mommy.' % field.__class__)

        # attributes like max_length, decimal_places are take in account when
        # generating the value.
        required_field_attrs = get_required_values(generator, field)
        return generator(**required_field_attrs)


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

            elif isinstance(item, basestring):
                rt[item] = getattr(field, item)

            else:
                raise ValueError("Required value '%s' is of wrong type. \
                                  Don't make mommy sad." % str(item))

    return rt
