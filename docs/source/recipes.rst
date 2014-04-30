Recipes
=======

If you're not comfortable with random data or even you just want to
improve the semantics of the generated data, there's hope for you.

You can define a recipe, which is a set of rules to generate data
for your models. Create a module called mommy_recipes.py at your app's
root directory: ::

    fixtures/
    migrations/
    templates/
    tests/
    __init__.py
    admin.py
    managers.py
    models.py
    mommy_recipes.py
    urls.py
    views.py


File: mommy_recipes.py ::

    from model_mommy.recipe import Recipe
    from family.models import Person

    person = Recipe(
        Person,
        name = 'John Doe',
        nickname = 'joe',
        age = 18,
        birthday = date.today(),
        appointment = datetime.now()
    )

.. note::

    You don't have to declare all the fields if you don't want to. Omitted fields will be generated automatically.


File: test_model.py ::

    # -*- coding:utf-8 -*-

    #Core Django imports
    from django.test import TestCase

    #Third-party app imports
    from model_mommy import mommy
    from model_mommy.recipe import Recipe, foreign_key

    # Relative imports of the 'app-name' package
    from .models import Person, Contact

    class PersonTestModel(TestCase):
        """
        Class to test the model
        Person
        """

        def setUp(self):
            """
            Set up all the tests
            """
            self.person_one = mommy.make_recipe(
                'family.person'
            )

            self.person_simpsons = Recipe(
                Person,
                name='Moe',
            )

            self.contact = Recipe(
                Contact,
                person=foreign_key(self.person_simpsons),
                tel='3333333eeeeR'
            )
    
            def test_kind_contact_create_instance(self):
                """
                True if create instance
                """
                contact = self.contact.make()
                self.assertIsInstance(contact, Contact)

Or if you don't want a persisted instance: ::

    from model_mommy import mommy

    mommy.prepare_recipe('family.person')


Another examples

.. note::

    You can use the _quantity parameter as well if you want to create more than one object from a single recipe.

.. note::
    
    You can define recipes locally to your module or test case as well. This can be useful for cases where a particular set of values may be unique to a particular test case, but used repeatedly there.


Look: 

File: mommy_recipes.py ::

    company_recipe = Recipe(Company, name='WidgetCo'

File: test_model.py ::

    class EmployeeTest(TestCase):
        def setUp(self):
            self.employee_recipe = Recipe(
                Employee,
                name=seq('Employee '),
                company=company_recipe.make()
            )

        def test_employee_list(self):
            self.employee_recipe.make(_quantity=3)
            # test stuff....

        def test_employee_tasks(self):
            employee1 = self.employee_recipe.make()
            task_recipe = Recipe(Task, employee=employee1)
            task_recipe.make(status='done')
            task_recipe.make(due_date=datetime(2014, 1, 1))
            # test stuff....

Recipes with foreign keys
-------------------------


