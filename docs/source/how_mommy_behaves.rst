How mommy behaves?
==================

By default, *model-mommy* skips fields with `null=True` or `blank=True`. Also if a field has a *default* value, it will be used.

You can override this behavior by:

1. Explicitly defining values

.. code-block:: python

    # from "Basic Usage" page, assume all fields either null=True or blank=True
    from .models import Kid  
    from model_mommy import mommy

    kid = mommy.make(Kid, happy=True, bio='Happy kid')
    
2. Passing `_fill_optional` with a list of fields to fill with random data

.. code-block:: python

    kid = mommy.make(Kid, _fill_optional=['happy', 'bio'])

3. Passing `_fill_optional=True` to fill all fields with random data

.. code-block:: python

    kid = mommy.make(Kid, _fill_optional=True)



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
