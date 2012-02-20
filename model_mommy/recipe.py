#coding: utf-8
from django.db.models import get_model

class Recipe(object):
    def __init__(self, model, **attrs):
        self.attr_mapping = attrs
        self.model = model

    def make(self):
        return self.model.objects.create(**self.attr_mapping)

