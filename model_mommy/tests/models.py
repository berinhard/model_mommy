#coding: utf-8
from django.db import models

class Kid(models.Model):
    name = models.CharField(max_length=30)
    age = models.IntegerField()
