from django.db.models.fields import BooleanField
from django.test import TestCase

from model_mommy import mommy
from model_mommy.generators import gen_from_list
from model_mommy.exceptions import CustomMommyNotFound, InvalidCustomMommy
from test.generic.models import Person

__all__ = ['SimpleExtendMommy', 'LessSimpleExtendMommy', 'CustomizeMommyClassViaSettings']


class SimpleExtendMommy(TestCase):

    def test_list_generator_respects_values_from_list(self):
        age_list = range(4, 12)

        class KidMommy(mommy.Mommy):
            attr_mapping = {'age': gen_from_list(age_list)}

        mom = KidMommy(Person)
        kid = mom.make()

        self.assertTrue(kid.age in age_list)


class LessSimpleExtendMommy(TestCase):

    def test_unexistent_required_field(self):
        gen_oposite = lambda x: not x
        gen_oposite.required = ['house']

        class SadPeopleMommy(mommy.Mommy):
            attr_mapping = {'happy': gen_oposite}

        mom = SadPeopleMommy(Person)
        self.assertRaises(AttributeError, mom.make)

    #TODO: put a better name
    def test_string_to_generator_required(self):
        gen_oposite = lambda default: not default
        gen_oposite.required = ['default']

        class SadPeopleMommy(mommy.Mommy):
            attr_mapping = {
                'happy': gen_oposite,
                'unhappy': gen_oposite,
            }

        happy_field = Person._meta.get_field('happy')
        unhappy_field = Person._meta.get_field('unhappy')
        mom = SadPeopleMommy(Person)
        person = mom.make()
        self.assertEqual(person.happy, not happy_field.default)
        self.assertEqual(person.unhappy, not unhappy_field.default)

    def test_fail_pass_non_string_to_generator_required(self):
        gen_age = lambda x: 10

        class MyMommy(mommy.Mommy):
            attr_mapping = {'age': gen_age}

        mom = MyMommy(Person)

        # for int
        gen_age.required = [10]
        self.assertRaises(ValueError, mom.make)

        # for float
        gen_age.required = [10.10]
        self.assertRaises(ValueError, mom.make)

        # for iterable
        gen_age.required = [[]]
        self.assertRaises(ValueError, mom.make)

        # for iterable/dict
        gen_age.required = [{}]
        self.assertRaises(ValueError, mom.make)

        # for boolean
        gen_age.required = [True]
        self.assertRaises(ValueError, mom.make)

class ClassWithoutMake(object):
    def prepare(self):
        pass

class ClassWithoutPrepare(object):
    def make(self):
        pass

class MommySubclass(mommy.Mommy):
    pass

class MommyDuck(object):
    def __init__(*args, **kwargs):
        pass

    def make(self):
        pass

    def prepare(self):
        pass

class CustomizeMommyClassViaSettings(TestCase):
    def class_to_import_string(self, class_to_convert):
        return '%s.%s' % (self.__module__, class_to_convert.__name__)

    def test_create_vanilla_mommy_used_by_default(self):
        mommy_instance = mommy.Mommy.create(Person)
        self.assertIs(mommy_instance.__class__, mommy.Mommy)

    def test_create_fail_on_custom_mommy_load_error(self):
        with self.settings(MOMMY_CUSTOM_CLASS='invalid_module.invalid_class'):
            self.assertRaises(CustomMommyNotFound, mommy.Mommy.create, Person)

    def test_create_fail_on_missing_required_functions(self):
        for invalid_mommy_class in [ClassWithoutMake, ClassWithoutPrepare]:
            with self.settings(MOMMY_CUSTOM_CLASS=self.class_to_import_string(invalid_mommy_class)):
                self.assertRaises(InvalidCustomMommy, mommy.Mommy.create, Person)

    def test_create_succeeds_with_valid_custom_mommy(self):
        for valid_mommy_class in [MommySubclass, MommyDuck]:
            with self.settings(MOMMY_CUSTOM_CLASS=self.class_to_import_string(valid_mommy_class)):
                custom_mommy_instance = mommy.Mommy.create(Person)
                self.assertIs(custom_mommy_instance.__class__, valid_mommy_class)
