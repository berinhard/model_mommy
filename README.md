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

You can also specify values for one or more attribute.

    another_kid = mommy.make_one(Kid, age = 3)
    assert another_kid.age == 3

But, if don't need a persisted object, mommy can handle this for you as well:

    from model_mommy import mommy
    from model_mommy.models import Kid

    kid = mommy.prepare_one(Kid)

It works like make_one, but like was said, it doesn't persist the instance.

## Extending Mommy

All attributes used to automatically populate mommy generated instances
are created with generators from **model_mommy/generators.py**. if you want
a specific field to be populated with a different generator from the default
generator, you must extend the mommy class to get this behavior. let's see a example:

    gen_newborn_age = lambda:0

    class BabeMommy(Mommy):
        attr_mapping = {'age':gen_newborn_age}

    mom = BabeMommy(Kid)
    baby = mom.make_one()
    assert(baby.age==0)

If the generator requires a attribute from the field as argument, you could do something like this:

    gen_name_from_default = lambda default_value:default_value
    gen_name_from_default.required = ['default']

You can also override the type_mapping, if you want to all values from a given Field to be populate with a value you prefer,
you  could do:

    class TimeCopMommy(Mommy):
        def __init__(self, model, fill_nullables=True):
            super(Mommy, self).__init__(model, fill_nullables)
            self.type_mapping[DateField] = datetime.date(2011, 02, 02)

## Doubts? Loved it? Hated it? Suggestions?

mail us!:
*  vanderson.mota **at** gmail **dot** com
*  italo.maia **at** gmail **dot** com

##Currently supports the fields:
CharField, TextField, FloatField, ForeignKey, Date and DateTimeField, BooleanField, URLField, and all the integer-type Fields

