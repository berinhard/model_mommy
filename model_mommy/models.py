#coding: utf-8

#######################################
# TESTING PURPOSE ONLY MODELS!!       #
# DO NOT ADD THE APP TO INSTALLED_APPS#
#######################################

from django.db import models

class Kid(models.Model):
    name = models.CharField(max_length=30)
    age = models.IntegerField()
    bio = models.TextField()
    wanted_games_qtd = models.BigIntegerField()
    birthday = models.DateField()

class Dog(models.Model):
    owner = models.ForeignKey('Kid')

class DummyIntModel(models.Model):
    int_field = models.IntegerField()
    big_int_field = models.BigIntegerField()
    small_int_field = models.SmallIntegerField()
    positive_small_int_field = models.PositiveSmallIntegerField()
    positive_int_field = models.PositiveIntegerField()

class DummyNumbersModel(models.Model):
    float_field = models.FloatField(null=True)
    decimal_field = models.DecimalField(max_digits=4, decimal_places=2, null=True)



