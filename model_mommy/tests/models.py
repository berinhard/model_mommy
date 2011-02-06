#coding: utf-8

#######################################
# TESTING PURPOSE ONLY MODELS!!       #
# DO NOT ADD THE APP TO INSTALLED_APPS#
#######################################

from django.db import models

# fix for django <= 1.1
if not hasattr(models, 'BigIntegerField'):
    setattr(models, 'BigIntegerField', models.IntegerField)

GENDER_CH = [('M', 'male'), ('F', 'female')]

class Person(models.Model):
    gender = models.CharField(max_length=1, choices=GENDER_CH)
    happy = models.BooleanField(default=True)
    name = models.CharField(max_length=30)
    age = models.IntegerField()
    bio = models.TextField()
    birthday = models.DateField()
    appointment = models.DateTimeField()
    wanted_games_qtd = models.BigIntegerField()

class Dog(models.Model):
    owner = models.ForeignKey('Person')
    breed = models.CharField(max_length=50)

class Store(models.Model):
    customers = models.ManyToManyField(Person, related_name='favorite_stores', blank=True, null=True)
    employees = models.ManyToManyField(Person, related_name='employers')

class DummyIntModel(models.Model):
    int_field = models.IntegerField()
    small_int_field = models.SmallIntegerField()
    big_int_field = models.BigIntegerField()

class DummyPositiveIntModel(models.Model):
    positive_small_int_field = models.PositiveSmallIntegerField()
    positive_int_field = models.PositiveIntegerField()

class DummyNumbersModel(models.Model):
    float_field = models.FloatField(null=True)

class DummyDecimalModel(models.Model):
    decimal_field = models.DecimalField(max_digits=5, decimal_places=2)
