# -*- coding:utf-8 -*-

import sys
import string
import datetime
from decimal import Decimal
from random import randint, choice, random

# retorna um dos valores da lista
gen_from_list = lambda L: choice(L)

# retorna um inteiro dentre o menor e o maior valor suportado pelo sistema
gen_integer = lambda lower=-sys.maxint, upper=sys.maxint: randint(lower, upper)

# gera um número float
gen_float = lambda:random()*gen_integer()

# gera um número decimal positivo 
gen_decimal = lambda max_digits, decimal_places: "%s.%s" % (
    ''.join([str(randint(0,9)) for i in range(max_digits-decimal_places)]), 
    ''.join([str(randint(0,9)) for i in range(decimal_places)]))

gen_decimal.required = ['max_digits', 'decimal_places']

gen_date = lambda: datetime.date.today()

gen_datetime = lambda: datetime.datetime.now()

gen_string = lambda max_length:''.join(choice(string.printable) for i in range(max_length))
gen_string.required = ['max_length']

gen_text = lambda max_length: lambda:''.join(choice(string.printable) for i in range(max_length))

# gera um valor booleano
gen_boolean = lambda: choice((True, False))
