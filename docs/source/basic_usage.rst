Basic Usage
===========

Let's say you have an app **family** with a model like this:

File: model.py ::

    class Kid(models.Model):
        """
        Model class Kid of family app
        """
        happy = models.BooleanField()
        name = models.CharField(max_length=30)
        age = models.IntegerField()
        bio = models.TextField()
        wanted_games_qtd = models.BigIntegerField()
        birthday = models.DateField()
        appointment = models.DateTimeField()

To create a persisted instance, just call Mommy:

File: test_model.py ::

    # -*- coding:utf-8 -*-

    #Core Django imports
    from django.test import TestCase

    #Third-party app imports
    from model_mommy import mommy
    from model_mommy.recipe import Recipe, foreign_key

    # Relative imports of the 'app-name' package
    from .models import Kid

    class KidTestModel(TestCase):
        """
        Class to test the model
        Kid
        """

        def setUp(self):
            """
            Set up all the tests
            """
            self.kid = mommy.make(Kid)


No need to pass attributes every damn time.

Importing every model over and over again is boring. So let Mommy import them for you: ::

    from model_mommy import mommy

    # 1st form: app_label.model_name
    kid = mommy.make('family.Kid')

    # 2nd form: model_name
    dog = mommy.make('Dog')

.. note::

    You can only use the 2nd form on unique model names. If you have an app family with a Dog, and an app farm with a Dog, you must use the app_label.model_name form.

.. note::

    model_name is case insensitive.
