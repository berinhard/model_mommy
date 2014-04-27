#coding: utf-8

#ATTENTION: Recipes defined for testing purposes only
from decimal import Decimal
from model_mommy.recipe import Recipe, foreign_key, seq
from model_mommy.recipe import related
from model_mommy.timezone import now
from test.generic.models import Person, Dog, DummyDefaultFieldsModel, DummyUniqueIntegerFieldModel

from six import u


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

serial_numbers_by = Recipe(DummyDefaultFieldsModel,
    default_decimal_field = seq(Decimal('20.1'), increment_by=Decimal('2.4')),
    default_int_field = seq(10, increment_by=3),
    default_float_field = seq(1.23, increment_by=1.8)
)

dog = Recipe(Dog,
    breed = 'Pug',
    owner = foreign_key(person)
)

other_dog = Recipe(Dog,
    breed = 'Basset',
    owner = foreign_key('person')
)

other_dog_unicode = Recipe(Dog,
    breed = 'Basset',
    owner = foreign_key(u('person'))
)

dummy_unique_field = Recipe(DummyUniqueIntegerFieldModel,
    value = seq(10),
)

dog_lady = Recipe(Person,
    dog_set = related('dog', other_dog)
)
