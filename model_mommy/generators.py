# -*- coding:utf-8 -*-

import sys
import string
import datetime
from decimal import Decimal
from random import randint, choice, random

MAX_LENGTH = 300

gen_from_list = choice

def gen_integer(min_int=-sys.maxint, max_int=sys.maxint):
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
