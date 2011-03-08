# -*- coding:utf-8 -*-

__doc__ = """
Generators are callables that return a value used to populate a field.

If this callable has a `required` attribute (a list, mostly), for each item in the list,
if the item is a string, the field attribute with the same name will be fetched from the field
and used as argument for the generator. If it is a callable (which will receive `field`
as first argument), it should return a list in the format (key, value) where key is
the argument name for generator and value is the value for that argument.
"""

import sys
import string
import datetime
from decimal import Decimal
from random import randint, choice, random

MAX_LENGTH = 300
# Using sys.maxint here breaks a bunch of tests when running against a
# Postgres database.
maxint = 10000

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
    choice_list = map(lambda x:x[0], C)
    return gen_from_list(choice_list)

def gen_integer(min_int=-maxint, max_int=maxint):
    return randint(min_int, max_int)

gen_float = lambda:random()*gen_integer()

def gen_decimal(max_digits, decimal_places):
    num_as_str = lambda x: ''.join([str(randint(0,9)) for i in range(x)])
    return "%s.%s" % (
        num_as_str(max_digits-decimal_places),
        num_as_str(decimal_places)
    )
gen_decimal.required = ['max_digits', 'decimal_places']

gen_date = datetime.date.today

gen_datetime = datetime.datetime.now

def gen_string(max_length):
    return ''.join(choice(string.printable) for i in range(max_length))
gen_string.required = ['max_length']

gen_text = lambda: gen_string(MAX_LENGTH)

gen_boolean = lambda: choice((True, False))

def gen_url():
    letters = ''.join(choice(string.letters) for i in range(30))
    return 'http://www.%s.com' % letters

gen_email = lambda: "%s@example.com" % gen_string(10)
