# -*- coding:utf-8 -*-
from decimal import Decimal

from django.test import TestCase
from django import VERSION
from django.db.models.options import Options
from django.db.models import Manager
from mock import patch
from model_mommy import mommy
from model_mommy import generators
from model_mommy.exceptions import ModelNotFound, AmbiguousModelName, InvalidQuantityException
from model_mommy.timezone import smart_datetime as datetime
from test.generic.models import Person, Dog, Store, LonelyPerson, School, SchoolEnrollment, ModelWithImpostorField, Classroom, GuardDog
from test.generic.models import User, PaymentBill
from test.generic.models import UnsupportedModel, DummyGenericRelationModel
from test.generic.models import DummyNullFieldsModel, DummyBlankFieldsModel
from test.generic.models import DummyDefaultFieldsModel, DummyMultipleInheritanceModel
from test.generic.models import DummyGenericForeignKeyModel, NonAbstractPerson


class ModelFinderTest(TestCase):
    def test_unicode_regression(self):
        obj = mommy.prepare(u'generic.Person')
        self.assertIsInstance(obj, Person)

    def test_model_class(self):
        obj = mommy.prepare(Person)
        self.assertIsInstance(obj, Person)

    def test_app_model_string(self):
        obj = mommy.prepare('generic.Person')
        self.assertIsInstance(obj, Person)

    def test_model_string(self):
        obj = mommy.prepare('Person')
        self.assertIsInstance(obj, Person)

    def test_raise_on_ambiguous_model_string(self):
        with self.assertRaises(AmbiguousModelName):
            obj = mommy.prepare('Ambiguous')

    def test_raise_model_not_found(self):
        with self.assertRaises(ModelNotFound):
            mommy.Mommy('non_existing.Model')

        with self.assertRaises(ModelNotFound):
            mommy.Mommy('NonExistingModel')


class MommyCreatesSimpleModel(TestCase):

    def test_consider_real_django_fields_only(self):
        id_ = ModelWithImpostorField._meta.get_field('id')
        with patch.object(mommy.Mommy, 'get_fields') as mock:
            f = Manager()
            f.name = 'foo'
            mock.return_value = [id_, f]
            try:
                mommy.make(ModelWithImpostorField)
            except TypeError:
                self.fail('TypeError raised')

    def test_make_should_create_one_object(self):
        person = mommy.make(Person)
        self.assertIsInstance(person, Person)

        # makes sure it is the person we created
        self.assertTrue(Person.objects.filter(id=person.id))

    def test_prepare_should_not_persist_one_object(self):
        person = mommy.prepare(Person)
        self.assertIsInstance(person, Person)

        # makes sure database is clean
        self.assertEqual(Person.objects.all().count(), 0)

        self.assertEqual(person.id, None)

    def test_make_one_should_create_one_object(self):
        """
        make_one method is deprecated, so this test must be removed when the
        method is removed
        """
        person = mommy.make_one(Person)
        self.assertIsInstance(person, Person)
        self.assertTrue(Person.objects.filter(id=person.id))

    def test_prepare_one_should_not_persist_one_object(self):
        """
        prepare_one method is deprecated, so this test must be removed when the
        method is removed
        """
        person = mommy.prepare_one(Person)
        self.assertIsInstance(person, Person)
        self.assertEqual(Person.objects.all().count(), 0)
        self.assertEqual(person.id, None)

    def test_non_abstract_model_creation(self):
        person = mommy.make(NonAbstractPerson, name='bob', happy=False)
        self.assertIsInstance(person, NonAbstractPerson)
        self.assertEqual('bob', person.name)
        self.assertFalse(person.happy)

    def test_multiple_inheritance_creation(self):
        multiple = mommy.make(DummyMultipleInheritanceModel)
        self.assertIsInstance(multiple, DummyMultipleInheritanceModel)
        self.assertTrue(Person.objects.filter(id=multiple.id))
        self.assertTrue(DummyDefaultFieldsModel.objects.filter(id=multiple.id))


class MommyRepeatedCreatesSimpleModel(TestCase):

    def test_make_should_create_objects_respecting_quantity_parameter(self):
        people = mommy.make(Person, _quantity=5)
        self.assertEqual(Person.objects.count(), 5)

        people = mommy.make(Person, _quantity=5, name="George Washington")
        self.assertTrue(all(p.name == "George Washington" for p in people))

    def test_make_raises_correct_exception_if_invalid_quantity(self):
        self.assertRaises(
            InvalidQuantityException, mommy.make, model=Person, _quantity="hi"
        )
        self.assertRaises(
            InvalidQuantityException, mommy.make, model=Person, _quantity=-1
        )

    def test_prepare_should_create_objects_respecting_quantity_parameter(self):
        people = mommy.prepare(Person, _quantity=5)
        self.assertEqual(len(people), 5)
        self.assertTrue(all(not p.id for p in people))

        people = mommy.prepare(Person, _quantity=5, name="George Washington")
        self.assertTrue(all(p.name == "George Washington" for p in people))

    def test_prepare_raises_correct_exception_if_invalid_quantity(self):
        self.assertRaises(
            InvalidQuantityException, mommy.prepare, model=Person, _quantity="hi"
        )
        self.assertRaises(
            InvalidQuantityException, mommy.prepare, model=Person, _quantity=-1
        )

    def test_make_many_method(self):
        """
        make_many method is deprecated, so this test must be removed when the
        method is removed
        """
        people = mommy.make_many(Person, quantity=5)
        self.assertEqual(Person.objects.count(), 5)

        people = mommy.make_many(Person, name="George Washington")
        self.assertTrue(all(p.name == "George Washington" for p in people))


class MommyCreatesAssociatedModels(TestCase):

    def test_dependent_models_with_ForeignKey(self):
        dog = mommy.make(Dog)
        self.assertIsInstance(dog.owner, Person)

    def test_foreign_key_on_parent_should_create_one_object(self):
        '''
        Foreign key on parent gets created twice. Once for
        parent oject and another time for child object
        '''
        person_count = Person.objects.count()
        dog = mommy.make(GuardDog)
        self.assertEqual(Person.objects.count(), person_count+1)

    def test_auto_now_add_on_parent_should_work(self):
        '''
        Foreign key on parent gets created twice. Once for
        parent oject and another time for child object
        '''
        person_count = Person.objects.count()
        dog = mommy.make(GuardDog)
        self.assertNotEqual(dog.created, None)

    def test_attrs_on_related_model_through_parent(self):
        '''
        Foreign key on parent gets created twice. Once for
        parent oject and another time for child object
        '''
        dog = mommy.make(GuardDog, owner__name='john')
        for person in Person.objects.all():
            self.assertEqual(person.name, 'john')

    def test_prepare_should_not_create_one_object(self):
        dog = mommy.prepare(Dog)
        self.assertIsInstance(dog, Dog)
        self.assertIsInstance(dog.owner, Person)

        # makes sure database is clean
        self.assertEqual(Person.objects.all().count(), 0)
        self.assertEqual(Dog.objects.all().count(), 0)

    def test_prepare_one_to_one_should_not_persist_one_object(self):
        lonely_person = mommy.prepare(LonelyPerson)

        # makes sure database is clean
        self.assertEqual(LonelyPerson.objects.all().count(), 0)
        self.assertTrue(isinstance(lonely_person.only_friend, Person))
        self.assertEqual(Person.objects.all().count(), 0)

    def test_create_one_to_one(self):
        lonely_person = mommy.make(LonelyPerson)

        self.assertEqual(LonelyPerson.objects.all().count(), 1)
        self.assertTrue(isinstance(lonely_person.only_friend, Person))
        self.assertEqual(Person.objects.all().count(), 1)

    def test_create_many_to_many_if_flagged(self):
        store = mommy.make(Store, make_m2m=True)
        self.assertEqual(store.employees.count(), 5)
        self.assertEqual(store.customers.count(), 5)

    def test_regresstion_many_to_many_field_is_accepted_as_kwargs(self):
        employees = mommy.make(Person, _quantity=3)
        customers = mommy.make(Person, _quantity=3)

        store = mommy.make(Store, employees=employees, customers=customers)

        self.assertEqual(store.employees.count(), 3)
        self.assertEqual(store.customers.count(), 3)
        self.assertEqual(Person.objects.count(), 6)

    def test_create_many_to_many_with_set_default_quantity(self):
        store = mommy.make(Store, make_m2m=True)
        self.assertEqual(store.employees.count(), mommy.MAX_MANY_QUANTITY)
        self.assertEqual(store.customers.count(), mommy.MAX_MANY_QUANTITY)

    def test_create_many_to_many_with_through_option(self):
        # School student's attr is a m2m relationship with a model through
        school = mommy.make(School, make_m2m=True)
        self.assertEqual(School.objects.count(), 1)
        self.assertEqual(school.students.count(), mommy.MAX_MANY_QUANTITY)
        self.assertEqual(SchoolEnrollment.objects.count(), mommy.MAX_MANY_QUANTITY)
        self.assertEqual(Person.objects.count(), mommy.MAX_MANY_QUANTITY)

    def test_does_not_create_many_to_many_as_default(self):
        store = mommy.make(Store, make_m2m=False)
        self.assertEqual(store.employees.count(), 0)
        self.assertEqual(store.customers.count(), 0)

    def test_does_not_create_nullable_many_to_many_for_relations(self):
        classroom = mommy.make(Classroom, make_m2m=False)
        self.assertEqual(classroom.students.count(), 0)

    def test_nullable_many_to_many_is_not_created_even_if_flagged(self):
        classroom = mommy.make(Classroom, make_m2m=True)
        self.assertEqual(classroom.students.count(), 0)

    def test_simple_creating_person_with_parameters(self):
        kid = mommy.make(Person, happy=True, age=10, name='Mike')
        self.assertEqual(kid.age, 10)
        self.assertEqual(kid.happy, True)
        self.assertEqual(kid.name, 'Mike')

    def test_creating_person_from_factory_using_paramters(self):
        person_mom = mommy.Mommy(Person)
        person = person_mom.make(happy=False, age=20, gender='M',
                                     name='John')
        self.assertEqual(person.age, 20)
        self.assertEqual(person.happy, False)
        self.assertEqual(person.name, 'John')
        self.assertEqual(person.gender, 'M')

    def test_ForeignKey_model_field_population(self):
        dog = mommy.make(Dog, breed='X1', owner__name='Bob')
        self.assertEqual('X1', dog.breed)
        self.assertEqual('Bob', dog.owner.name)

    def test_ForeignKey_model_field_population_should_work_with_prepare(self):
        dog = mommy.prepare(Dog, breed='X1', owner__name='Bob')
        self.assertEqual('X1', dog.breed)
        self.assertEqual('Bob', dog.owner.name)

    def test_ForeignKey_model_field_population_for_not_required_fk(self):
        user = mommy.make(User, profile__email="a@b.com")
        self.assertEqual('a@b.com', user.profile.email)

    def test_does_not_creates_null_ForeignKey(self):
        user = mommy.make(User)
        self.assertFalse(user.profile)

    def test_ensure_recursive_ForeignKey_population(self):
        bill = mommy.make(PaymentBill, user__profile__email="a@b.com")
        self.assertEqual('a@b.com', bill.user.profile.email)

    def test_field_lookup_for_m2m_relationship(self):
        store = mommy.make(Store, suppliers__gender='M')
        suppliers = store.suppliers.all()
        self.assertTrue(suppliers)
        for supplier in suppliers:
            self.assertEqual('M', supplier.gender)

    def test_field_lookup_for_one_to_one_relationship(self):
        lonely_person = mommy.make(LonelyPerson, only_friend__name='Bob')
        self.assertEqual('Bob', lonely_person.only_friend.name)

    def test_allow_create_fkey_related_model(self):
        try:
            person = mommy.make(Person, dog_set=[mommy.prepare(Dog), mommy.prepare(Dog)])
        except TypeError:
            self.fail('type error raised')

        self.assertEqual(person.dog_set.count(), 2)

class HandlingUnsupportedModels(TestCase):
    def test_unsupported_model_raises_an_explanatory_exception(self):
        try:
            mommy.make(UnsupportedModel)
            self.fail("Should have raised a TypeError")
        except TypeError as e:
            self.assertTrue('not supported' in repr(e))


class HandlingModelsWithGenericRelationFields(TestCase):
    def test_create_model_with_generic_relation(self):
        dummy = mommy.make(DummyGenericRelationModel)
        self.assertIsInstance(dummy, DummyGenericRelationModel)


class HandlingContentTypeField(TestCase):
    def test_create_model_with_contenttype_field(self):
        dummy = mommy.make(DummyGenericForeignKeyModel)
        self.assertIsInstance(dummy, DummyGenericForeignKeyModel)


class SkipNullsTestCase(TestCase):
    def test_skip_null(self):
        dummy = mommy.make(DummyNullFieldsModel)
        self.assertEqual(dummy.null_foreign_key, None)
        self.assertEqual(dummy.null_integer_field, None)


class SkipBlanksTestCase(TestCase):
    def test_skip_blank(self):
        dummy = mommy.make(DummyBlankFieldsModel)
        self.assertEqual(dummy.blank_char_field, '')
        self.assertEqual(dummy.blank_text_field, '')


class SkipDefaultsTestCase(TestCase):
    def test_skip_fields_with_default(self):
        dummy = mommy.make(DummyDefaultFieldsModel)
        self.assertEqual(dummy.default_char_field, 'default')
        self.assertEqual(dummy.default_text_field, 'default')
        self.assertEqual(dummy.default_int_field, 123)
        self.assertEqual(dummy.default_float_field, 123.0)
        self.assertEqual(dummy.default_date_field, '2012-01-01')
        self.assertEqual(dummy.default_date_time_field, datetime(2012, 1, 1))
        self.assertEqual(dummy.default_time_field, '00:00:00')
        self.assertEqual(dummy.default_decimal_field, Decimal('0'))
        self.assertEqual(dummy.default_email_field, 'foo@bar.org')
        self.assertEqual(dummy.default_slug_field, 'a-slug')


if VERSION < (1, 4):
    from test.generic.forms import DummyIPAddressFieldForm

    class MommyGeneratesIPAdresses(TestCase):
        def test_create_model_with_valid_ipv4(self):
            form_data = {
                'ip': generators.gen_ipv4(),
            }
            self.assertTrue(DummyIPAddressFieldForm(form_data).is_valid())
else:
    from test.generic.forms import DummyGenericIPAddressFieldForm

    class MommyGeneratesIPAdresses(TestCase):
        def test_create_model_with_valid_ipv4(self):
            form_data = {
                'ip': generators.gen_ipv4(),
            }
            self.assertTrue(DummyGenericIPAddressFieldForm(form_data).is_valid())

        def test_create_model_with_valid_ipv6(self):
            form_data = {
                'ip': generators.gen_ipv6(),
            }
            self.assertTrue(DummyGenericIPAddressFieldForm(form_data).is_valid())
