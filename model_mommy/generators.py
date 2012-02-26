# -*- coding:utf-8 -*-

__doc__ = """
Generators are callables that return a value used to populate a field.

If this callable has a `required` attribute (a list, mostly), for each item in
the list, if the item is a string, the field attribute with the same name will
be fetched from the field and used as argument for the generator. If it is a
callable (which will receive `field` as first argument), it should return a
list in the format (key, value) where key is the argument name for generator
and value is the value for that argument.
"""

import string
import datetime
from decimal import Decimal
from random import randint, choice, random

from django.contrib.contenttypes.models import ContentType
from django.db.models import get_models
from django.core.files import File

import os
from os.path import abspath, join, dirname


MAX_LENGTH = 300
# Using sys.maxint here breaks a bunch of tests when running against a
# Postgres database.
MAX_INT = 10000

def gen_file_field():
    file_path = abspath(join(dirname(__file__),'mock_file.txt'))
    fixture_txt_file = File(open(file_path))
    return fixture_txt_file

def gen_from_list(L):
    '''Makes sure all values of the field are generated from the list L
    Usage:
    from mommy import Mommy
    class KidMommy(Mommy):
      attr_mapping = {'some_field':gen_from_list([A, B, C])}
    '''
    return lambda: choice(L)

# -- DEFAULT GENERATORS --


def gen_from_choices(C):
    choice_list = map(lambda x: x[0], C)
    return gen_from_list(choice_list)


def gen_integer(min_int=-MAX_INT, max_int=MAX_INT):
    return randint(min_int, max_int)


def gen_float():
    return random() * gen_integer()


def gen_decimal(max_digits, decimal_places):
    num_as_str = lambda x: ''.join([str(randint(0, 9)) for i in range(x)])
    return Decimal("%s.%s" % (num_as_str(max_digits - decimal_places),
                              num_as_str(decimal_places)))
gen_decimal.required = ['max_digits', 'decimal_places']

gen_date = datetime.date.today

gen_datetime = datetime.datetime.now


def gen_time():
    return datetime.datetime.now().time()


def gen_string(max_length):
    return ''.join(choice(string.printable) for i in range(max_length))
gen_string.required = ['max_length']


def gen_slug(max_length=50):
    valid_chars = string.letters + string.digits + '_-'
    return ''.join(choice(valid_chars) for i in range(max_length))


def gen_text():
    return gen_string(MAX_LENGTH)


def gen_boolean():
    return choice((True, False))


def gen_url():
    return 'http://www.%s.com' % gen_string(30)


def gen_email():
    return "%s@example.com" % gen_string(10)


def gen_content_type():
    return ContentType.objects.get_for_model(choice(get_models()))
