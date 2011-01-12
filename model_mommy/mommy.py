# -*- coding: utf-8 -*-
from django.db.models.fields import AutoField, CharField, TextField
from django.db.models.fields import DateField, DateTimeField
from django.db.models.fields import IntegerField, BigIntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField, PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField
from django.db.models.fields import BooleanField

from django.db.models import ForeignKey

from string import letters
from random import choice, randint
from datetime import date
from decimal import Decimal
import generators 
import sys

MAX_LENGTH = 300

def make_one(model, attrs=None):
    mommy = Mommy(model)
    return mommy.make_one(attrs or {})

make_one.required = [lambda field: (field.related.parent_model, 'model')]

default_mapping = {
    BooleanField:generators.gen_boolean,
    IntegerField:generators.gen_integer,
    BigIntegerField:generators.gen_integer,
    SmallIntegerField:generators.gen_integer,
    
    PositiveIntegerField:lambda: generators.gen_integer(0), 
    PositiveSmallIntegerField:lambda: generators.gen_integer(0),
    
    FloatField:generators.gen_float,
    DecimalField:generators.gen_decimal,
    
    CharField:generators.gen_string,
    TextField:generators.gen_text(MAX_LENGTH),
    
    ForeignKey:make_one,
    
    DateField:generators.gen_date,
    DateTimeField:generators.gen_date,
}

class Mommy(object):
    model = None
    attr_mapping = None
    type_mapping = default_mapping
    
    def __init__(self, model=None):
        if model is not None:
            self.model = model
        
        if self.model is None:
            raise ValueError("Mommy wants to know her kids better. Inform the 'model' class, sweetie!")
    
    def make_one(self, attrs=None):
        attrs = attrs or {}
        
        for field in self.model._meta.fields:
            if isinstance(field, AutoField):
                continue
            
            if field.name not in attrs:
                attrs[field.name] = self.generate_value(field)
        return self.model.objects.create(**attrs)
    
    def generate_value(self, field):
        'Calls the generator associated with a field passing all required args.'
        if self.attr_mapping is not None and field.name in self.attr_mapping:
            generator = self.attr_mapping[field.name]
        else:
            generator = self.type_mapping[field.__class__]
        
        required_fields = get_required_values(generator, field)
        return generator(**required_fields)

def get_required_values(generator, field):
    '''
    Gets required values for a generator from the field.
    If required value is a function, call's it with field as argument.
    If required value is a string, simple fetch the value from the field
    and returns.
    '''
    rt = {}
    if hasattr(generator, 'required'):
        for item in generator.required:
            
            if callable(item): # mommy can deal with the nasty hacking too!
                value, attr_name = item(field)
                rt[attr_name] = value
            
            elif isinstance(item, basestring):
                rt[item] = getattr(field, item)
            
            else: raise ValueError("Required value '%s' is of wrong type. Don't make mommy sad." % str(item))
    return rt
