Model Relationships
===================

Mommy also handles relationships. Say the kid has a dog:

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
        
        class Meta:
            verbose_name = _(u'Kid')
            verbose_name_plural = _(u'Kids')

        def __unicode__(self):
            """
            Retorn the name of kid 
            """
            return u'%s' % (self.name)

    class Dog(models.Model):
        """
        Model class Dog of family app
        """
        owner = models.ForeignKey('Kid')

when you ask Mommy:

File: test_model.py ::

    # -*- coding:utf-8 -*-

    #Core Django imports
    from django.test import TestCase

    #Third-party app imports
    from model_mommy import mommy
    from model_mommy.recipe import Recipe, foreign_key

    # Relative imports of the 'app-name' package

    class DogTestModel(TestCase):
        """
        Class to test the model
        Dog
        """

        def setUp(self):
            """
            Set up all the tests
            """
            self.rex = mommy.make('family.Dog')

She will also create the Kid, automagically.


M2M Relationships
-----------------

File: test_model.py ::

    # -*- coding:utf-8 -*-

    #Core Django imports
    from django.test import TestCase

    #Third-party app imports
    from model_mommy import mommy
    from model_mommy.recipe import Recipe, foreign_key

    # Relative imports of the 'app-name' package

    class DogTestModel(TestCase):
        """
        Class to test the model
        Dog
        """

        def setUp(self):
            """
            Set up all the tests
            """
            self.rex = mommy.make('family.Dog', M2M=True)


