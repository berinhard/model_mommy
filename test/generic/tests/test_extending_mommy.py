from django.db.models.fields import BooleanField
from django.test import TestCase

from model_mommy import mommy
from model_mommy.models import Person
from model_mommy.generators import gen_from_list

__all__ = ['SimpleExtendMommy', 'LessSimpleExtendMommy']


class SimpleExtendMommy(TestCase):

    def test_list_generator_respects_values_from_list(self):
        age_list = range(4, 12)

        class KidMommy(mommy.Mommy):
            attr_mapping = {'age': gen_from_list(age_list)}

        mom = KidMommy(Person)
        kid = mom.make_one()

        self.assertTrue(kid.age in age_list)

    def test_type_mapping_overwriting_boolean_model_behavior(self):
        class SadPeopleMommy(mommy.Mommy):
            def __init__(self, model):
                super(SadPeopleMommy, self).__init__(model)
                self.type_mapping.update({BooleanField: lambda: False})

        assert Person._meta.get_field('happy').default is True
        sad_people_mommy = SadPeopleMommy(Person)
        person = sad_people_mommy.make_one()

        self.assertEqual(person.happy, False)


class LessSimpleExtendMommy(TestCase):

    def test_unexistent_required_field(self):
        gen_oposite = lambda x: not x
        gen_oposite.required = ['house']

        class SadPeopleMommy(mommy.Mommy):
            attr_mapping = {'happy': gen_oposite}

        mom = SadPeopleMommy(Person)
        self.assertRaises(AttributeError, mom.make_one)

    #TODO: put a better name
    def test_string_to_generator_required(self):
        gen_oposite = lambda default: not default
        gen_oposite.required = ['default']

        class SadPeopleMommy(mommy.Mommy):
            attr_mapping = {'happy': gen_oposite}

        happy_field = Person._meta.get_field('happy')
        mom = SadPeopleMommy(Person)
        person = mom.make_one()
        self.assertEqual(person.happy, not happy_field.default)

    def test_fail_pass_non_string_to_generator_required(self):
        gen_age = lambda x: 10

        class MyMommy(mommy.Mommy):
            attr_mapping = {'age': gen_age}

        mom = MyMommy(Person)

        # for int
        gen_age.required = [10]
        self.assertRaises(ValueError, mom.make_one)

        # for float
        gen_age.required = [10.10]
        self.assertRaises(ValueError, mom.make_one)

        # for iterable
        gen_age.required = [[]]
        self.assertRaises(ValueError, mom.make_one)

        # for iterable/dict
        gen_age.required = [{}]
        self.assertRaises(ValueError, mom.make_one)

        # for boolean
        gen_age.required = [True]
        self.assertRaises(ValueError, mom.make_one)
