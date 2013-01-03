# Model Mommy: Smart fixtures for better tests

*Model-mommy* offers you a smart way to create fixtures for testing in Django.
With a simple and powerful API you can create many objects with a single line of code.


## Install

```console
pip install model_mommy
```


## Basic usage

Let's say you have an app **family** with a model like this:

```python
class Kid(models.Model):
    happy = models.BooleanField()
    name = models.CharField(max_length=30)
    age = models.IntegerField()
    bio = models.TextField()
    wanted_games_qtd = models.BigIntegerField()
    birthday = models.DateField()
    appointment = models.DateTimeField()
```

To create a persisted instance, just call *Mommy*:

```python
from model_mommy import mommy
from family.models import Kid

kid = mommy.make_one(Kid)
```

No need to pass attributes every damn time.

Importing every model over and over again is boring. So let *Mommy* import them for you:

```python
    from model_mommy import mommy

    kid = mommy.make_one('family.Kid')
```

Note that you must use `app_label.model_name`. The `model_name` is case insensitive.


### Model Relationships

*Mommy* also handles relationships. Say the kid has a dog:

```python
class Dog(models.Model):
    owner = models.ForeignKey('Kid')
```

when you ask *Mommy*:

```python
from model_mommy import mommy

rex = mommy.make_one('family.Dog')
```

She will also create the `Kid`, automagically.


### Defining some attributes

Of course it's possible to explicitly set values for attributes.

```python
from model_mommy import mommy

another_kid = mommy.make_one('family.Kid', age=3)
```

Related objects attributes are also reachable:

```python
from model_mommy import mommy

bobs_dog = mommy.make_one('family.Dog', owner__name='Bob')
```


### Non persistent objects

If don't need a persisted object, *Mommy* can handle this for you as well:

```python
from model_mommy import mommy

kid = mommy.prepare_one('family.Kid')
```

It works like `make_one`, but it doesn't persist the instance.

## How mommy behaves?

model_mommy skips fields with null=True or blank=True. Also if the field has a default value, mommy will use it.

## When you shouldn't let mommy do the things for you:

If you have a field that has any special validation, you should set the value by yourself.
model_mommy should be used to handle the fields that doesn't have relation with the test that you're doing at the moment and don't require special validation(like unique, etc), but still required in order to create the object.

###Currently supports the fields:
BooleanField, IntegerField, BigIntegerField, SmallIntegerField, PositiveIntegerField, PositiveSmallIntegerField, FloatField, DecimalField, CharField, TextField, SlugField, ForeignKey, OneToOneField, ManyToManyField, DateField, DateTimeField, TimeField, URLField, EmailField, FileField and ImageField.

## Recipes
If you're not confortable with random data, or you have some custom fields, or even you just want to improve the semantics of data generation, there's hope for you.
You can define a recipe, which is a set of rules to generate data for your models. You create a module called mommy_recipes.py at the app root:

```python
from model_mommy.recipe import Recipe

person = Recipe(Person,
    name = 'John Doe',
    nickname = 'joe',
    age = 18,
    birthday = date.today(),
    appointment = datetime.now()
)
```

The variable 'person' serves as the recipe name, which will be used for data creation when you call:

```python
from model_mommy import mommy
mommy.make_recipe('model_mommy.person')
```

Or if you don't want a persisted model:

```python
mommy.prepare_recipe('model_mommy.person')
```

Where 'model_mommy' is the app name and 'person' is the recipe name

### ForeignKeys

You can also define foreign_key relations:

```python
dog = Recipe(Dog,
    breed = 'Pug',
    owner = foreign_key(person)
)
```

Notice that 'person' is a recipe. You may be thinking: "I can put the Person model instance directly in the owner field": And yes, you can. But i recommend using the foreign_key function for 2 reasons:

  * Semantics: You know it's an foreign_key relation when you're reading
  * The associated model will be created only when you call 'make_recipe' and not during recipe definition

### Passing Callables

You can also pass callables as arguments, so that the values will be generated during 'make_recipe':

```python
callable = date.today
person = Recipe(Person,
    name = 'John Doe',
    nickname = 'joe',
    age = 18,
    birthday = callable,
)
```

### Overriding recipe definitions
You can have different values when calling **make_recipe** or **prepare_recipe**. This is useful when you have to create multiple objects and you have some unique field, for instance. You just have to pass the values as keyword args, like this:

```python
mommy.make_recipe('model_mommy.person', name='Peter Parker')
```

#
## Doubts? Loved it? Hated it? Suggestions?

Mail us!:

 *  vanderson.mota **at** gmail **dot** com
 *  italo.maia **at** gmail **dot** com

# Hacking

### 1. prepare a virtual environment

```console
pip install virtualenvwrapper
mkvirtualenv --no-site-packages --distribute
```

### 2. install the requirements

```console
pip install -r requirements.txt
```

### 3. run the tests

```console
make test
```
