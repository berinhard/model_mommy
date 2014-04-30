Defining some attributes
========================

Of course it's possible to explicitly set values for attributes.

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
            self.kid = mommy.make(
                Kid,
                age=3
            )

            self.another_kid = mommy.make(
                'family.Kid',
                age=6
            )

Related objects attributes are also reachable:

File: test_model.py ::

    # -*- coding:utf-8 -*-

    #Core Django imports
    from django.test import TestCase

    #Third-party app imports
    from model_mommy import mommy
    from model_mommy.recipe import Recipe, foreign_key

    # Relative imports of the 'app-name' package
    from .models import Dog

    class DogTestModel(TestCase):
        """
        Class to test the model
        Dog
        """

        def setUp(self):
            """
            Set up all the tests
            """

            self.bobs_dog = mommy.make(
                'family.Dog',
                owner__name='Bob'
            )
