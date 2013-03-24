#coding: utf-8

#ATTENTION: Recipes defined for testing purposes only
from decimal import Decimal
from model_mommy.recipe import Recipe, foreign_key, seq
from model_mommy.timezone import now
from test.generic.models import Person, Dog, DummyDefaultFieldsModel


person = Recipe(Person,
    name = 'John Doe',
    nickname = 'joe',
    age = 18,
    bio = 'Someone in the crowd',
    blog = 'http://joe.blogspot.com',
    wanted_games_qtd = 4,
    birthday = now().date(),
    appointment = now(),
    birth_time = now()
)

serial_person = Recipe(Person,
    name = seq('joe'),
)

serial_numbers = Recipe(DummyDefaultFieldsModel,
    default_decimal_field = seq(Decimal('20.1')),
    default_int_field = seq(10),
    default_float_field = seq(1.23)
)

dog = Recipe(Dog,
    breed = 'Pug',
    owner = foreign_key(person)
)

other_dog = Recipe(Dog,
    breed = 'Basset',
    owner = foreign_key('person')
)

