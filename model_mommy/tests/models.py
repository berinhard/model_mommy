#coding: utf-8

#######################################
# TESTING PURPOSE ONLY MODELS!!       #
# DO NOT ADD THE APP TO INSTALLED_APPS#
#######################################

from django.db import models

GENDER_CH = [('M', 'male'), ('F', 'female')]

class Person(models.Model):
    gender = models.CharField(max_length=1, choices=GENDER_CH)
    happy = models.BooleanField(default=True)
    name = models.CharField(max_length=30)
    age = models.IntegerField()
    bio = models.TextField()
    birthday = models.DateField()
    appointment = models.DateTimeField()

    #backward compatibilty with Django 1.1
    try:
        wanted_games_qtd = models.BigIntegerField()
    except AttributeError:
        wanted_games_qtd = models.IntegerField()

class Dog(models.Model):
    owner = models.ForeignKey('Person')
    breed = models.CharField(max_length=50)

class DummyIntModel(models.Model):
    int_field = models.IntegerField()
    small_int_field = models.SmallIntegerField()

    #backward compatibilty with Django 1.1
    try:
        big_int_field = models.BigIntegerField()
    except AttributeError:
        big_int_field = models.IntegerField()

class DummyPositiveIntModel(models.Model):
    positive_small_int_field = models.PositiveSmallIntegerField()
    positive_int_field = models.PositiveIntegerField()

class DummyNumbersModel(models.Model):
    float_field = models.FloatField(null=True)

class DummyDecimalModel(models.Model):
    decimal_field = models.DecimalField(max_digits=5, decimal_places=2)
