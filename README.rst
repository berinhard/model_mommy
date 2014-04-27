============================================
Model Mommy: Smart fixtures for better tests
============================================

*Model-mommy* offers you a smart way to create fixtures for testing in Django.
With a simple and powerful API you can create many objects with a single line of code.

.. image:: https://travis-ci.org/vandersonmota/model_mommy.png?branch=master
        :target: https://travis-ci.org/vandersonmota/model_mommy

Install
=======

.. code-block:: console

    pip install model_mommy


Basic usage
===========

Let's say you have an app **family** with a model like this:

.. code-block:: python

    class Kid(models.Model):
        happy = models.BooleanField()
        name = models.CharField(max_length=30)
        age = models.IntegerField()
        bio = models.TextField()
        wanted_games_qtd = models.BigIntegerField()
        birthday = models.DateField()
        appointment = models.DateTimeField()

To create a persisted instance, just call *Mommy*:

.. code-block:: python

    from model_mommy import mommy
    from family.models import Kid

    kid = mommy.make(Kid)

No need to pass attributes every damn time.

Importing every model over and over again is boring. So let *Mommy* import them for you:

.. code-block:: python

    from model_mommy import mommy

    # 1st form: app_label.model_name
    kid = mommy.make('family.Kid')

    # 2nd form: model_name
    dog = mommy.make('Dog')


.. [1] You can only use the 2nd form on unique model names. If you have an app
       *family* with a *Dog*, and an app *farm* with a *Dog*, you must use the
       `app_label.model_name` form.

.. [2] `model_name` is case insensitive.


Model Relationships
-------------------

*Mommy* also handles relationships. Say the kid has a dog:

.. code-block:: python

    class Dog(models.Model):
        owner = models.ForeignKey('Kid')

when you ask *Mommy*:

.. code-block:: python

    from model_mommy import mommy

    rex = mommy.make('family.Dog')

She will also create the `Kid`, automagically.


Defining some attributes
------------------------

Of course it's possible to explicitly set values for attributes.

.. code-block:: python

    from model_mommy import mommy

    another_kid = mommy.make('family.Kid', age=3)

Related objects attributes are also reachable:

.. code-block:: python

    from model_mommy import mommy

    bobs_dog = mommy.make('family.Dog', owner__name='Bob')


Non persistent objects
----------------------

If don't need a persisted object, *Mommy* can handle this for you as well:

.. code-block:: python

    from model_mommy import mommy

    kid = mommy.prepare('family.Kid')

It works like `make`, but it doesn't persist the instance.

More than one instance
----------------------

If you need to create more than one instance of the model, you can use the `_quantity` parameter for it:

.. code-block:: python

    from model_mommy import mommy

    kids = mommy.make('family.Kid', _quantity=3)
    assert len(kids) == 3

It also works with `prepare`:

.. code-block:: python

    from model_mommy import mommy

    kids = mommy.prepare('family.Kid', _quantity=3)
    assert len(kids) == 3

How mommy behaves?
==================

By default, *model-mommy* skips fields with `null=True` or `blank=True`. Also if a field has a *default* value, it will be used.

You can override this behavior by explicitly defining values.


When shouldn't you let mommy generate things for you?
-----------------------------------------------------

If you have fields with special validation, you should set their values by yourself.

*Model-mommy* should handle fields that:

1. don't matter for the test you're writing;
2. don't require special validation (like unique, etc);
3. are required to create the object.


Currently supported fields
--------------------------

* BooleanField, IntegerField, BigIntegerField, SmallIntegerField, PositiveIntegerField, PositiveSmallIntegerField, FloatField, DecimalField
* CharField, TextField, SlugField, URLField, EmailField
* ForeignKey, OneToOneField, ManyToManyField (even with through model)
* DateField, DateTimeField, TimeField
* FileField, ImageField

Custom fields
-------------

Model-mommy allows you to define generators methods for your custom fields or overrides its default generators. This could be achieved by specifing a dict on settings that its keys are the field paths and the values their generators functions, as the example bellow:

.. code-block:: python

    # on your settings.py file:
    def gen_func():
        return 'value'

    MOMMY_CUSTOM_FIELDS_GEN = {
        'test.generic.fields.CustomField': gen_func,
    }

Recipes
=======

If you're not comfortable with random data or even you just want to improve the semantics of the generated data, there's hope for you.

You can define a **recipe**, which is a set of rules to generate data for your models. Create a module called `mommy_recipes.py` at your app's root directory:

.. code-block:: python

    from model_mommy.recipe import Recipe
    from family.models import Person

    person = Recipe(Person,
        name = 'John Doe',
        nickname = 'joe',
        age = 18,
        birthday = date.today(),
        appointment = datetime.now()
    )

Note you don't have to declare all the fields if you don't want to. Omitted fields will be generated automatically.

The variable `person` serves as the recipe name:

.. code-block:: python

    from model_mommy import mommy

    mommy.make_recipe('family.person')

Or if you don't want a persisted instance:

.. code-block:: python

    from model_mommy import mommy

    mommy.prepare_recipe('family.person')

You can use the `_quantity` parameter as well if you want to create more than one object from a single recipe.


You can define recipes locally to your module or test case as well. This can be useful for cases where a particular set of values may be unique to a particular test case, but used repeatedly there.

.. code-block:: python

    company_recipe = Recipe(Company, name='WidgetCo')

    class EmployeeTest(TestCase):
        def setUp(self):
            self.employee_recipe = Recipe(
                Employee, name=seq('Employee '),
                company=company_recipe.make())

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

You can define `foreign_key` relations:

.. code-block:: python

    from model_mommy.recipe import Recipe, foreign_key
    from family.models import Person, Dog


    person = Recipe(Person,
        name = 'John Doe',
        nickname = 'joe',
        age = 18,
        birthday = date.today(),
        appointment = datetime.now()
    )

    dog = Recipe(Dog,
        breed = 'Pug',
        owner = foreign_key(person)
    )

Notice that `person` is a *recipe*.

You may be thinking: "I can put the Person model instance directly in the owner field". That's not recommended.

Using the `foreign_key` is important for 2 reasons:

* Semantics. You'll know that attribute is a foreign key when you're reading;
* The associated instance will be created only when you call `make_recipe` and not during recipe definition;

You can also use `related`, when you want two or more models to share the same parent:

.. code-block:: python


    from model_mommy.recipe import related, Recipe

    dog = Recipe(Dog,
        breed = 'Pug',
    )
    other_dog = Recipe(Dog,
        breed = 'Boxer',
    )
    person_with_three_dogs = Recipe(Person,
        dog_set = related('dog', 'other_dog')
    )

Note this will only work when calling `make_recipe` because the related manager requires the objects in the related_set to be persisted. That said, calling `prepare_recipe` the related_set will be empty.

Recipes with callables
----------------------

It's possible to use *callables* as recipe's attribute value.

.. code-block:: python

    from datetime import date
    from model_mommy.recipe import Recipe
    from family.models import Person

    person = Recipe(Person,
        birthday = date.today,
    )

When you call `make_recipe`, *Mommy* will set the attribute to the value returned by the callable.


Recipes with iterators
----------------------

You can also use *iterators* (including *generators*) to provide multiple values to a recipe.

.. code-block:: python

    from itertools import cycle

    colors = ['red', 'green', 'blue', 'yellow']
    person = Recipe(Person,
        favorite_color = cycle(colors)
    )

*Mommy* will use the next value in the *iterator* every time you create a model from the recipe.

Sequences in recipes
--------------------

Sometimes, you have a field with an unique value and using `make` can cause random errors. Also, passing an attribute value just to avoid uniqueness validation problems can be tedious. To solve this you can define a sequence with `seq`

.. code-block:: python


    from model_mommy.recipe import Recipe, seq
    from family.models import Person

    person = Recipe(Person,
        name = seq('Joe'),
        age = seq(15)
    )

    p = mommy.make_recipe('myapp.person')
    p.name
    >>> 'Joe1'
    p.age
    >>> 16

    p = mommy.make_recipe('myapp.person')
    p.name
    >>> 'Joe2'
    p.age
    >>> 17

This will append a counter to strings to avoid uniqueness problems and it will sum the counter with numerical values.


You can also provide an optional `increment_by` argument which will modify incrementing behaviour. This can be an integer, float or Decimal.

.. code-block:: python


    person = Recipe(Person,
        age = seq(15, increment_by=3)
        height_ft = seq(5.5, increment_by=.25)
    )

    p = mommy.make_recipe('myapp.person')
    p.age
    >>> 18
    p.height_ft
    >>> 5.75

    p = mommy.make_recipe('myapp.person')
    p.age
    >>> 21
    p.height_ft
    >>> 6.0


Overriding recipe definitions
-----------------------------

Passing values when calling `make_recipe` or `prepare_recipe` will override the recipe rule.

.. code-block:: python

    from model_mommy import mommy

    mommy.make_recipe('model_mommy.person', name='Peter Parker')

This is useful when you have to create multiple objects and you have some unique field, for instance.


Deprecation Warnings
====================

Because of the changes of model_mommy's API, the following methods are deprecated and will be removed in one of the future releases:

  * `mommy.make_one` -> should use the method `mommy.make` instead
  * `mommy.prepare_one` -> should use the method `mommy.prepare` instead
  * `mommy.make_many` -> should use the method `mommy.make` with the `_quantity` parameter instead
  * `mommy.make_many_from_recipe` -> should use the method `mommy.make_recipe` with the `_quantity` parameter instead

Known Issues
============

django-taggit
-------------

Model-mommy identifies django-taggit's `TaggableManager` as a normal Django field, which can lead to errors:

.. code-block:: pycon

    TypeError: <class 'taggit.managers.TaggableManager'> is not supported by mommy.

The fix for this is to set ``blank=True`` on your ``TaggableManager``.

Extensions
==========

GeoDjango
---------
Works with it? This project has some custom generators for it:
https://github.com/sigma-consultoria/mommy_spatial_generators


Contributing
============

1. Prepare a virtual environment.

.. code-block:: console

    pip install virtualenvwrapper
    mkvirtualenv --no-site-packages --distribute

2. Install the requirements.

.. code-block:: console

    pip install -r requirements.txt

3. Run the tests.

.. code-block:: console

    make test


Inspiration
===========

*Model-mommy* was inspired by many great open source software like ruby's ObjectDaddy and FactoryGirl.


Doubts? Loved it? Hated it? Suggestions?
========================================

Join our mailing list for support, development and ideas!

*  https://groups.google.com/group/model-mommy
