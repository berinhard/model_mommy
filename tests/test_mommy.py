import pytest
import datetime
from decimal import Decimal
from unittest.mock import patch

from django.db.models import Manager
from django.db.models.signals import m2m_changed

from model_mommy import mommy
from model_mommy import random_gen
from model_mommy.exceptions import ModelNotFound, AmbiguousModelName, InvalidQuantityException
from model_mommy.timezone import smart_datetime

from tests.generic import models
from tests.generic.forms import DummyGenericIPAddressFieldForm


class TestsModelFinder():

    def test_unicode_regression(self):
        obj = mommy.prepare('generic.Person')
        assert isinstance(obj, models.Person)

    def test_model_class(self):
        obj = mommy.prepare(models.Person)
        assert isinstance(obj, models.Person)

    def test_app_model_string(self):
        obj = mommy.prepare('generic.Person')
        assert isinstance(obj, models.Person)

    def test_model_string(self):
        obj = mommy.prepare('Person')
        assert isinstance(obj, models.Person)

    def test_raise_on_ambiguous_model_string(self):
        with pytest.raises(AmbiguousModelName):
            mommy.prepare('Ambiguous')

    def test_raise_model_not_found(self):
        with pytest.raises(ModelNotFound):
            mommy.Mommy('non_existing.Model')

        with pytest.raises(ModelNotFound):
            mommy.Mommy('NonExistingModel')


@pytest.mark.django_db
class TestsMommyCreatesSimpleModel():

    def test_consider_real_django_fields_only(self):
        id_ = models.ModelWithImpostorField._meta.get_field('id')
        with patch.object(mommy.Mommy, 'get_fields') as mock:
            f = Manager()
            f.name = 'foo'
            mock.return_value = [id_, f]
            try:
                mommy.make(models.ModelWithImpostorField)
            except TypeError:
                assert False, 'TypeError raised'

    def test_make_should_create_one_object(self):
        person = mommy.make(models.Person)
        assert isinstance(person, models.Person)

        # makes sure it is the person we created
        assert models.Person.objects.filter(id=person.id).exists()

    def test_prepare_should_not_persist_one_object(self):
        person = mommy.prepare(models.Person)
        assert isinstance(person, models.Person)

        # makes sure database is clean
        assert not models.Person.objects.all().exists()
        assert person.id is None

    def test_non_abstract_model_creation(self):
        person = mommy.make(models.NonAbstractPerson, name='bob', happy=False)
        assert isinstance(person, models.NonAbstractPerson)
        assert 'bob' == person.name
        assert person.happy is False

    def test_abstract_model_subclass_creation(self):
        instance = mommy.make(models.SubclassOfAbstract)
        assert isinstance(instance, models.SubclassOfAbstract)
        assert isinstance(instance, models.AbstractModel)
        assert isinstance(instance.name, type(u''))
        assert len(instance.name) == 30
        assert isinstance(instance.height, int)

    def test_multiple_inheritance_creation(self):
        multiple = mommy.make(models.DummyMultipleInheritanceModel)
        assert isinstance(multiple, models.DummyMultipleInheritanceModel)
        assert models.Person.objects.filter(id=multiple.id).exists()
        assert models.DummyDefaultFieldsModel.objects.filter(
            default_id=multiple.default_id
        ).exists()


@pytest.mark.django_db
class TestsMommyRepeatedCreatesSimpleModel():

    def test_make_should_create_objects_respecting_quantity_parameter(self):
        people = mommy.make(models.Person, _quantity=5)
        assert models.Person.objects.count() == 5

        people = mommy.make(models.Person, _quantity=5, name="George Washington")
        assert all(p.name == "George Washington" for p in people)

    def test_make_raises_correct_exception_if_invalid_quantity(self):
        with pytest.raises(InvalidQuantityException):
            mommy.make(_model=models.Person, _quantity="hi")
        with pytest.raises(InvalidQuantityException):
            mommy.make(_model=models.Person, _quantity=-1)
        with pytest.raises(InvalidQuantityException):
            mommy.make(_model=models.Person, _quantity=0)

    def test_prepare_should_create_objects_respecting_quantity_parameter(self):
        people = mommy.prepare(models.Person, _quantity=5)
        assert len(people) == 5
        assert all(not p.id for p in people)

        people = mommy.prepare(models.Person, _quantity=5, name="George Washington")
        assert all(p.name == "George Washington" for p in people)

    def test_prepare_raises_correct_exception_if_invalid_quantity(self):
        with pytest.raises(InvalidQuantityException):
            mommy.prepare(_model=models.Person, _quantity="hi")
        with pytest.raises(InvalidQuantityException):
            mommy.prepare(_model=models.Person, _quantity=-1)
        with pytest.raises(InvalidQuantityException):
            mommy.prepare(_model=models.Person, _quantity=0)


@pytest.mark.django_db
class TestMommyPrepareSavingRelatedInstances():

    def test_default_behaviour_for_and_fk(self):
        dog = mommy.prepare(models.Dog)

        assert dog.pk is None
        assert dog.owner.pk is None
        with pytest.raises(ValueError):
            dog.friends_with

    def test_create_fk_instances(self):
        dog = mommy.prepare(models.Dog, _save_related=True)

        assert dog.pk is None
        assert dog.owner.pk
        with pytest.raises(ValueError):
            dog.friends_with

    def test_create_fk_instances_with_quantity(self):
        dog1, dog2 = mommy.prepare(models.Dog, _save_related=True, _quantity=2)

        assert dog1.pk is None
        assert dog1.owner.pk
        with pytest.raises(ValueError):
            dog1.friends_with

        assert dog2.pk is None
        assert dog2.owner.pk
        with pytest.raises(ValueError):
            dog2.friends_with

    def test_create_one_to_one(self):
        lonely_person = mommy.prepare(models.LonelyPerson, _save_related=True)

        assert lonely_person.pk is None
        assert lonely_person.only_friend.pk


@pytest.mark.django_db
class TestMommyCreatesAssociatedModels():

    def test_dependent_models_with_ForeignKey(self):
        dog = mommy.make(models.Dog)
        assert isinstance(dog.owner, models.Person)

    def test_foreign_key_on_parent_should_create_one_object(self):
        '''
        Foreign key on parent gets created twice. Once for
        parent object and another time for child object
        '''
        person_count = models.Person.objects.count()
        mommy.make(models.GuardDog)
        assert models.Person.objects.count() == person_count + 1

    def test_foreign_key_on_parent_is_not_created(self):
        '''
        Foreign key on parent doesn't get created using owner
        '''
        owner = mommy.make(models.Person)
        person_count = models.Person.objects.count()
        dog = mommy.make(models.GuardDog, owner=owner)
        assert models.Person.objects.count() == person_count
        assert dog.owner == owner

    def test_foreign_key_on_parent_id_is_not_created(self):
        '''
        Foreign key on parent doesn't get created using owner_id
        '''
        owner = mommy.make(models.Person)
        person_count = models.Person.objects.count()
        dog = mommy.make(models.GuardDog, owner_id=owner.id)
        assert models.Person.objects.count() == person_count
        assert models.GuardDog.objects.get(pk=dog.pk).owner == owner

    def test_auto_now_add_on_parent_should_work(self):
        '''
        Foreign key on parent gets created twice. Once for
        parent object and another time for child object
        '''
        person_count = models.Person.objects.count()
        dog = mommy.make(models.GuardDog)
        assert models.Person.objects.count() == person_count + 1
        assert dog.created

    def test_attrs_on_related_model_through_parent(self):
        '''
        Foreign key on parent gets created twice. Once for
        parent object and another time for child object
        '''
        mommy.make(models.GuardDog, owner__name='john')
        for person in models.Person.objects.all():
            assert person.name == 'john'

    def test_access_related_name_of_m2m(self):
        try:
            mommy.make(models.Person, classroom_set=[mommy.make(models.Classroom)])
        except TypeError:
            assert False, 'type error raised'

    def test_save_object_instances_when_handling_one_to_many_relations(self):
        owner = mommy.make(models.Person)
        dogs_set = mommy.prepare(
            models.Dog,
            owner=owner,
            _quantity=2,
        )

        assert 0 == models.Dog.objects.count()  # ensure there're no dogs in our db
        home = mommy.make(
            models.Home,
            owner=owner,
            dogs=dogs_set,
        )
        assert home.dogs.count() == 2
        assert 2 == models.Dog.objects.count()  # dogs in dogs_set were created

    def test_prepare_fk(self):
        dog = mommy.prepare(models.Dog)
        assert isinstance(dog, models.Dog)
        assert isinstance(dog.owner, models.Person)

        assert models.Person.objects.all().count() == 0
        assert models.Dog.objects.all().count() == 0

    def test_create_one_to_one(self):
        lonely_person = mommy.make(models.LonelyPerson)

        assert models.LonelyPerson.objects.all().count() == 1
        assert isinstance(lonely_person.only_friend, models.Person)
        assert models.Person.objects.all().count() == 1

    def test_create_many_to_many_if_flagged(self):
        store = mommy.make(models.Store, make_m2m=True)
        assert store.employees.count() == 5
        assert store.customers.count() == 5

    def test_regresstion_many_to_many_field_is_accepted_as_kwargs(self):
        employees = mommy.make(models.Person, _quantity=3)
        customers = mommy.make(models.Person, _quantity=3)

        store = mommy.make(models.Store, employees=employees, customers=customers)

        assert store.employees.count() == 3
        assert store.customers.count() == 3
        assert models.Person.objects.count() == 6

    def test_create_many_to_many_with_set_default_quantity(self):
        store = mommy.make(models.Store, make_m2m=True)
        assert store.employees.count() == mommy.MAX_MANY_QUANTITY
        assert store.customers.count() == mommy.MAX_MANY_QUANTITY

    def test_create_many_to_many_with_through_option(self):
        """
         This does not works
        """
        # School student's attr is a m2m relationship with a model through
        school = mommy.make(models.School, make_m2m=True)
        assert models.School.objects.count() == 1
        assert school.students.count() == mommy.MAX_MANY_QUANTITY
        assert models.SchoolEnrollment.objects.count() == mommy.MAX_MANY_QUANTITY
        assert models.Person.objects.count() == mommy.MAX_MANY_QUANTITY

    def test_does_not_create_many_to_many_as_default(self):
        store = mommy.make(models.Store)
        assert store.employees.count() == 0
        assert store.customers.count() == 0

    def test_does_not_create_nullable_many_to_many_for_relations(self):
        classroom = mommy.make(models.Classroom, make_m2m=False)
        assert classroom.students.count() == 0

    def test_nullable_many_to_many_is_not_created_even_if_flagged(self):
        classroom = mommy.make(models.Classroom, make_m2m=True)
        assert not classroom.students.count()

    def test_m2m_changed_signal_is_fired(self):
        # TODO: Use object attrs instead of mocks for Django 1.4 compat
        self.m2m_changed_fired = False

        def test_m2m_changed(*args, **kwargs):
            self.m2m_changed_fired = True

        m2m_changed.connect(test_m2m_changed, dispatch_uid='test_m2m_changed')
        mommy.make(models.Store, make_m2m=True)
        assert self.m2m_changed_fired

    def test_simple_creating_person_with_parameters(self):
        kid = mommy.make(models.Person, happy=True, age=10, name='Mike')
        assert kid.age == 10
        assert kid.happy == True
        assert kid.name == 'Mike'

    def test_creating_person_from_factory_using_paramters(self):
        person_mom = mommy.Mommy(models.Person)
        person = person_mom.make(happy=False, age=20, gender='M', name='John')
        assert person.age == 20
        assert person.happy == False
        assert person.name == 'John'
        assert person.gender == 'M'

    def test_ForeignKey_model_field_population(self):
        dog = mommy.make(models.Dog, breed='X1', owner__name='Bob')
        assert 'X1' == dog.breed
        assert 'Bob' == dog.owner.name

    def test_ForeignKey_model_field_population_should_work_with_prepare(self):
        dog = mommy.prepare(models.Dog, breed='X1', owner__name='Bob')
        assert 'X1' == dog.breed
        assert 'Bob' == dog.owner.name

    def test_ForeignKey_model_field_population_for_not_required_fk(self):
        user = mommy.make(models.User, profile__email="a@b.com")
        assert 'a@b.com' == user.profile.email

    def test_does_not_creates_null_ForeignKey(self):
        user = mommy.make(models.User)
        assert not user.profile

    def test_passing_m2m_value(self):
        store = mommy.make(models.Store, customers=[mommy.make(models.Person)])
        assert store.customers.count() == 1

    def test_ensure_recursive_ForeignKey_population(self):
        bill = mommy.make(models.PaymentBill, user__profile__email="a@b.com")
        assert 'a@b.com' == bill.user.profile.email

    def test_field_lookup_for_m2m_relationship(self):
        store = mommy.make(models.Store, suppliers__gender='M')
        suppliers = store.suppliers.all()
        assert suppliers
        for supplier in suppliers:
            assert 'M' == supplier.gender

    def test_field_lookup_for_one_to_one_relationship(self):
        lonely_person = mommy.make(models.LonelyPerson, only_friend__name='Bob')
        assert 'Bob' == lonely_person.only_friend.name

    def test_allow_create_fkey_related_model(self):
        try:
            person = mommy.make(models.Person, dog_set=[mommy.make(models.Dog),
                                                        mommy.make(models.Dog)])
        except TypeError:
            assert False, 'type error raised'

        assert person.dog_set.count() == 2

    def test_field_lookup_for_related_field(self):
        person = mommy.make(
            models.Person,
            one_related__name='Foo',
            fk_related__name='Bar',
        )

        assert person.pk
        assert person.one_related.pk
        assert 1, person.fk_related.count()
        assert 'Foo' == person.one_related.name
        assert 'Bar' == person.fk_related.get().name

    def test_field_lookup_for_related_field_does_not_work_with_prepare(self):
        person = mommy.prepare(
            models.Person,
            one_related__name='Foo',
            fk_related__name='Bar',
        )

        assert not person.pk
        assert 0 == models.RelatedNamesModel.objects.count()


@pytest.mark.django_db
class TestHandlingUnsupportedModels():

    def test_unsupported_model_raises_an_explanatory_exception(self):
        try:
            mommy.make(models.UnsupportedModel)
            assert False, "Should have raised a TypeError"
        except TypeError as e:
            assert 'not supported' in repr(e)


@pytest.mark.django_db
class TestHandlingModelsWithGenericRelationFields():

    def test_create_model_with_generic_relation(self):
        dummy = mommy.make(models.DummyGenericRelationModel)
        assert isinstance(dummy, models.DummyGenericRelationModel)


@pytest.mark.django_db
class TestHandlingContentTypeField():
    def test_create_model_with_contenttype_field(self):
        dummy = mommy.make(models.DummyGenericForeignKeyModel)
        assert isinstance(dummy, models.DummyGenericForeignKeyModel)


@pytest.mark.django_db
class TestHandlingContentTypeFieldNoQueries():
    def test_create_model_with_contenttype_field(self):
        dummy = mommy.prepare(models.DummyGenericForeignKeyModel)
        assert isinstance(dummy, models.DummyGenericForeignKeyModel)


@pytest.mark.django_db
class TestSkipNullsTestCase():

    def test_skip_null(self):
        dummy = mommy.make(models.DummyNullFieldsModel)
        assert dummy.null_foreign_key is None
        assert dummy.null_integer_field is None


@pytest.mark.django_db
class TestFillNullsTestCase():

    def test_create_nullable_many_to_many_if_flagged_and_fill_field_optional(self):
        classroom = mommy.make(models.Classroom, make_m2m=True, _fill_optional=[
            'students'])
        assert classroom.students.count() == 5

    def test_create_nullable_many_to_many_if_flagged_and_fill_optional(self):
        classroom = mommy.make(models.Classroom, make_m2m=True, _fill_optional=True)
        assert classroom.students.count() == 5

    def test_nullable_many_to_many_is_not_created_if_not_flagged_and_fill_optional(self):
        classroom = mommy.make(models.Classroom, make_m2m=False, _fill_optional=True)
        assert classroom.students.count() == 0


@pytest.mark.django_db
class TestSkipBlanksTestCase():

    def test_skip_blank(self):
        dummy = mommy.make(models.DummyBlankFieldsModel)
        assert dummy.blank_char_field == ''
        assert dummy.blank_text_field == ''


@pytest.mark.django_db
class TestFillBlanksTestCase():

    def test_fill_field_optional(self):
        dummy = mommy.make(models.DummyBlankFieldsModel, _fill_optional=['blank_char_field'])
        assert len(dummy.blank_char_field) == 50

    def test_fill_wrong_field(self):
        with pytest.raises(AttributeError) as exc_info:
            mommy.make(models.DummyBlankFieldsModel,_fill_optional=['blank_char_field', 'wrong'])

        msg = "_fill_optional field(s) ['wrong'] are not related to model DummyBlankFieldsModel"
        assert msg in str(exc_info.value)

    def test_fill_wrong_fields_with_parent(self):
        with pytest.raises(AttributeError):
            mommy.make(models.SubclassOfAbstract, _fill_optional=['name', 'wrong'])

    def test_fill_many_optional(self):
        dummy = mommy.make(
            models.DummyBlankFieldsModel,
            _fill_optional=['blank_char_field', 'blank_text_field']
        )
        assert len(dummy.blank_text_field) == 300

    def test_fill_all_optional(self):
        dummy = mommy.make(models.DummyBlankFieldsModel, _fill_optional=True)
        assert len(dummy.blank_char_field) == 50
        assert len(dummy.blank_text_field) == 300

    def test_fill_optional_with_integer(self):
        with pytest.raises(TypeError):
            mommy.make(models.DummyBlankFieldsModel, _fill_optional=1)


@pytest.mark.django_db
class TestFillAutoFieldsTestCase():

    def test_fill_autofields_with_provided_value(self):
        mommy.make(models.DummyEmptyModel, id=237)
        saved_dummy = models.DummyEmptyModel.objects.get()
        assert saved_dummy.id == 237

    def test_keeps_prepare_autovalues(self):
        dummy = mommy.prepare(models.DummyEmptyModel, id=543)
        assert dummy.id == 543
        dummy.save()
        saved_dummy = models.DummyEmptyModel.objects.get()
        assert saved_dummy.id == 543


@pytest.mark.django_db
class TestSkipDefaultsTestCase():

    def test_skip_fields_with_default(self):
        dummy = mommy.make(models.DummyDefaultFieldsModel)
        assert dummy.default_char_field == 'default'
        assert dummy.default_text_field == 'default'
        assert dummy.default_int_field == 123
        assert dummy.default_float_field == 123.0
        assert dummy.default_date_field == '2012-01-01'
        assert dummy.default_date_time_field == smart_datetime(2012, 1, 1)
        assert dummy.default_time_field == '00:00:00'
        assert dummy.default_decimal_field == Decimal('0')
        assert dummy.default_email_field == 'foo@bar.org'
        assert dummy.default_slug_field == 'a-slug'


@pytest.mark.django_db
class TestMommyHandlesModelWithNext():

    def test_creates_instance_for_model_with_next(self):
        instance = mommy.make(
            models.BaseModelForNext,
            fk=mommy.make(models.ModelWithNext),
        )

        assert instance.id
        assert instance.fk.id
        assert instance.fk.attr
        assert 'foo' == instance.fk.next()


@pytest.mark.django_db
class TestMommyHandlesModelWithList():

    def test_creates_instance_for_model_with_list(self):
        instance = mommy.make(models.BaseModelForList, fk=["foo"])

        assert instance.id
        assert ["foo"] == instance.fk


@pytest.mark.django_db
class TestMommyGeneratesIPAdresses():

    def test_create_model_with_valid_ips(self):
        form_data = {
            'ipv4_field': random_gen.gen_ipv4(),
            'ipv6_field': random_gen.gen_ipv6(),
            'ipv46_field': random_gen.gen_ipv46(),
        }
        assert DummyGenericIPAddressFieldForm(form_data).is_valid()


@pytest.mark.django_db
class TestMommyAllowsSaveParameters():

    def test_allows_save_kwargs_on_mommy_make(self):
        owner = mommy.make(models.Person)
        dog = mommy.make(models.ModelWithOverridedSave, _save_kwargs={'owner': owner})
        assert owner == dog.owner

        dog1, dog2 = mommy.make(
            models.ModelWithOverridedSave,
            _save_kwargs={'owner': owner},
            _quantity=2
        )
        assert owner == dog1.owner
        assert owner == dog2.owner


@pytest.mark.django_db
class TestMommyAutomaticallyRefreshFromDB():

    def test_refresh_from_db_if_true(self):
        person = mommy.make(models.Person, birthday='2017-02-01', _refresh_after_create=True)

        assert person.birthday == datetime.date(2017, 2, 1)

    def test_do_not_refresh_from_db_if_false(self):
        person = mommy.make(models.Person, birthday='2017-02-01', _refresh_after_create=False)

        assert person.birthday == '2017-02-01'
        assert person.birthday != datetime.date(2017, 2, 1)

    def test_do_not_refresh_from_db_by_default(self):
        person = mommy.make(models.Person, birthday='2017-02-01')

        assert person.birthday == '2017-02-01'
        assert person.birthday != datetime.date(2017, 2, 1)


@pytest.mark.django_db
class TestMommyMakeCanFetchInstanceFromDefaultManager():

    def test_annotation_within_manager_get_queryset_are_run_on_make(self):
        '''Test that a custom model Manager can be used within make().

        Passing _from_manager='objects' will force mommy.make() to
        return an instance that has been going through that given
        Manager, thus calling its get_queryset() method and associated
        code, like default annotations. As such the instance will have
        the same fields as one created in the application.

        '''
        movie = mommy.make(models.MovieWithAnnotation)
        with pytest.raises(AttributeError):
            movie.name

        movie = mommy.make(
            models.MovieWithAnnotation,
            title='Old Boy',
            _from_manager='objects',
        )
        assert movie.title == movie.name
