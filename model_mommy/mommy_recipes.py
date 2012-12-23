#coding: utf-8

#ATTENTION: Recipes defined for testing purposes only
from model_mommy.recipe import Recipe, foreign_key
from model_mommy.models import Person, Dog
from model_mommy.timezone import now


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

dog = Recipe(Dog,
    breed = 'Pug',
    owner = foreign_key(person)
)

other_dog = Recipe(Dog,
    breed = 'Basset',
    owner = foreign_key('person')
)
