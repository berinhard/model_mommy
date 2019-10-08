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
* CharField, TextField, BinaryField, SlugField, URLField, EmailField, IPAddressField, GenericIPAddressField
* ForeignKey, OneToOneField, ManyToManyField (even with through model)
* DateField, DateTimeField, TimeField
* FileField, ImageField
* JSONField, ArrayField, HStoreField

Require ``django.contrib.gis`` in ``INSTALLED_APPS``:

* GeometryField, PointField, LineStringField, PolygonField, MultiPointField, MultiLineStringField, MultiPolygonField, GeometryCollectionField

Custom fields
-------------

Model-mommy allows you to define generators methods for your custom fields or overrides its default generators.
This could be achieved by specifing the field and generator function for the `generators.add` function.
Both can be the real python objects imported in settings or just specified as import path string.

Examples:

.. code-block:: python

    from model_mommy import mommy

    def gen_func():
        return 'value'

    mommy.generators.add('test.generic.fields.CustomField', gen_func)

.. code-block:: python

    # in the module code.path:
    def gen_func():
        return 'value'

    # in your tests.py file:
    from model_mommy import mommy

    mommy.generators.add('test.generic.fields.CustomField', 'code.path.gen_func')

Customizing Mommy
-----------------

In some rare cases, you might need to customize the way Mommy behaves.
This can be achieved by creating a new class and specifying it in your settings files. It is likely that you will want to extend Mommy, however the minimum requirement is that the custom class have `make` and `prepare` functions.
In order for the custom class to be used, make sure to use the `model_mommy.mommy.make` and `model_mommy.mommy.prepare` functions, and not `model_mommy.mommy.Mommy` directly.

Examples:

.. code-block:: python

    # in the module code.path:
    class CustomMommy(mommy.Mommy)
        def get_fields(self):
            return [
                field
                for field in super(CustomMommy, self).get_fields()
                if not field isinstance CustomField
            ]

    # in your settings.py file:
    MOMMY_CUSTOM_CLASS = 'code.path.CustomMommy'


Additionaly, if you want to your created instance to be returned respecting one of your custom ModelManagers, you can use the `_from_manager` parameter as the example bellow:


.. code-block:: python

    movie = mommy.make(Movie, title='Old Boys', _from_manager='availables')  # This will use the Movie.availables model manager


Save method custom parameters
-----------------------------

If you have overwritten the `save` method for a model, you can pass custom parameters to it using model mommy. Example:

.. code-block:: python

    class ProjectWithCustomSave(models.Model)
        # some model fields
        created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

        def save(self, user, *args, **kwargs):
            self.created_by = user
            return super(ProjectWithCustomSave, self).save(*args, **kwargs)

    #with model mommy:
    user = mommy.make(settings.AUTH_USER_MODEL)
    project = mommy.make(ProjectWithCustomSave, _save_kwargs={'user': user})
    assert user == project.user
