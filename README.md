# Creating objects for testing shouldn't hurt

model_mommy is a tool for creating objects for testing in Django, inspired in ruby's ObjectDaddy and FactoryGirl.
It generate the values according with the field type, but i will add support to custom values as well.

#Installing

    pip install model_mommy

## Basic Usage:

If you have a model like this in your app:

    class Kid(models.Model):
        happy = models.BooleanField()
        name = models.CharField(max_length=30)
        age = models.IntegerField()
        bio = models.TextField()
        wanted_games_qtd = models.BigIntegerField()
        birthday = models.DateField()
        appointment = models.DateTimeField()

just call the mommy =):

    from model_mommy import mommy
    from model_mommy.models import Kid

    kid = mommy.make_one(Kid)


and your object is created! No boring attributes passing like 'foobar' every damn time.


mommy also handles relationships. Suppose the kid has a dog:

    class Dog(models.Model):
        owner = models.ForeignKey('Kid')

when you do:

    rex = mommy.make_one(Dog)

it will also create the Kid, automatically.

You can also pass arguments to make one.

    another_kid = mommy.make_one(Kid, {'age':3})
    assert(another_kid.age == 3)

But, if don't need a persisted object, mommy can handle this for you as well:

    from model_mommy import mommy
    from model_mommy.models import Kid

    kid = mommy.prepare_one(Kid)

It works like make_one, but like was said, it doesn't persist the instance.

## Not so Basic Usage:

Model instances can also be generated from Mommy factories. Make your
mass producer mom like this:

    from model_mommy.mommy import Mommy
    from model_mommy.models import Kid

    mom = Mommy(Kid)
    first_kid = mom.make_one()
    second_kid = mom.make_one()
    third_kid = mom.make_one()

Note that this kind of construction is much more efficient than
mommy.make_one(Model), so, if you need to create a lot of instances,
this much be a nicier approach.

## Even Less Basic Usage

All attributes used to automatically populate mommy generated instances
are created with generators from **model_mommy/generators.py**. If you want
a specific field to be populated with a different generator from the default
generator, you must extend the Mommy class to get this behavior. Let's see a example:

    from model_mommy.generators import gen_from_list
    from model_mommy.models import Kid
    from model_mommy.mommy import Mommy

    a_lot_of_games = range(30, 100)

    class HardGamerMommy(Mommy):
        attr_mapping = {
            'wanted_games_qtd':gen_from_list(a_lot_of_games)
        }

    mom = HardGamerMommy(Kid)
    kid = mom.make_one()
    assert(kid.wanted_games_qtd in a_lot_of_games)

You can also change the default generator for a field. Let's take a look:

    from random import randint
    from model_mommy.models import Kid
    from model_mommy.mommy import Mommy

    class KidMommy(Mommy):
        attr_mapping = {
            'wanted_games_qtd':gen_from_list(a_lot_of_games)
        }

    mom = HardGamerMommy(Kid)
    kid = mom.make_one()
    assert(kid.wanted_games_qtd in a_lot_of_games)

Note that you can also create your own generator.

## Your Own Generator

A generator is just a simple callable (like a function) that may require a few arguments.
Let's see a dead simple example:

    gen_newborn_age = lambda:0

    class BabeMommy(Mommy):
        attr_mapping = {'age':gen_newborn_age}

    mom = BabeMommy(Kid)
    baby = mom.make_one()
    assert(baby.age==0)

If the generator requires a attribute of field as argument, you could do something like this:

    gen_name_from_default = lambda default_value:default_value
    gen_name_from_default.required = ['default']

For more examples, see tests.

##Currently supports the fields:
CharField, TextField, FloatField, ForeignKey, Date and DateTimeField, BooleanField, and all the integer-type Fields
