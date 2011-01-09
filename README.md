# Creating objects for testing shouldn't hurt
-----------------------------------------------------------

model_mommy is a tool for creating objects for testing in Django, inspired in ruby's ObjectDaddy and FactoryGirl.
It generate the values according with the field type, but it supports custom values as well.

#Installing

    pip install model_mommy

## Basic Usage:

If you have a model like this in your app:

    class Kid(models.Model):
        name = models.CharField(max_length=30)
        age = models.IntegerField()
        bio = models.TextField()
        birthday = models.DateField()

just call the mommy =):

    from model_mommy import mommy
    kid = mommy.make_one(Kid)

and your object is created! No boring attributes passing like 'foobar' every damn time.

mommy also handles relationships. Suppose the kid has a dog:

    class Dog(models.Model):
        owner = models.ForeignKey('Kid')

when you do:

    rex = mommy.make_one(Dog)

it will also create the Kid, automatically.

##Currently supports the fields:
CharField, TextField, FloatField, ForeignKey, and all the integer-type Fields
