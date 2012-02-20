#coding: utf-8

#ATTENTION: Recipes defined for testing purposes only
from model_mommy.recipe import Recipe
from model_mommy.models import Person

from datetime import date, datetime

person = Recipe(Person,
  name = 'John Doe',
  nickname = 'joe',
  age = 18,
  bio = 'Someone in the crowd',
  blog = 'http://joe.blogspot.com',
  wanted_games_qtd = 4,
  birthday = date.today(),
  appointment = datetime.now()
)
