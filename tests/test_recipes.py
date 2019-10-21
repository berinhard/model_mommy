import pytest
import itertools
from random import choice
from decimal import Decimal
from unittest.mock import patch

from datetime import timedelta
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key, RecipeForeignKey
from model_mommy.timezone import now, tz_aware
from model_mommy.exceptions import InvalidQuantityException, RecipeIteratorEmpty
from tests.generic.models import TEST_TIME, Person, DummyNumbersModel, DummyBlankFieldsModel, Dog
from tests.generic.mommy_recipes import SmallDogRecipe, pug

recipe_attrs = {
    'name': 'John Doe',
    'nickname': 'joe',
    'age': 18,
    'bio': 'Someone in the crowd',
    'birthday': now().date(),
    'appointment': now(),
    'blog': 'http://joe.blogspot.com',
    'wanted_games_qtd': 4,
    'birth_time': now()
}
person_recipe = Recipe(Person, **recipe_attrs)

@pytest.mark.django_db
class TestDefiningRecipes():

    def test_import_seq_from_mommy(self):
        """
            Import seq method directly from mommy module
        """
        try:
            from model_mommy import seq  # NoQA
        except ImportError:
            self.fail('{} raised'.format(ImportError.__name__))

    def test_flat_model_make_recipe_with_the_correct_attributes(self):
        """
          A 'flat model' means a model without associations, like
          foreign keys, many to many and one to one
        """
        person = person_recipe.make()
        assert person.name == recipe_attrs['name']
        assert person.nickname == recipe_attrs['nickname']
        assert person.age == recipe_attrs['age']
        assert person.bio == recipe_attrs['bio']
        assert person.birthday == recipe_attrs['birthday']
        assert person.appointment == recipe_attrs['appointment']
        assert person.blog == recipe_attrs['blog']
        assert person.wanted_games_qtd == recipe_attrs['wanted_games_qtd']
        assert person.id is not None

    def test_flat_model_prepare_recipe_with_the_correct_attributes(self):
        person = person_recipe.prepare()
        assert person.name == recipe_attrs['name']
        assert person.nickname == recipe_attrs['nickname']
        assert person.age == recipe_attrs['age']
        assert person.bio == recipe_attrs['bio']
        assert person.birthday == recipe_attrs['birthday']
        assert person.appointment == recipe_attrs['appointment']
        assert person.blog == recipe_attrs['blog']
        assert person.wanted_games_qtd == recipe_attrs['wanted_games_qtd']
        assert person.id is None

    def test_accepts_callable(self):
        r = Recipe(
            DummyBlankFieldsModel,
            blank_char_field=lambda: 'callable!!'
        )
        value = r.make().blank_char_field
        assert value == 'callable!!'

    def test_always_calls_when_creating(self):
        with patch('tests.test_recipes.choice') as choice_mock:
            choice_mock.return_value = 'foo'
            lst = ['foo', 'bar', 'spam', 'eggs']
            r = Recipe(
                DummyBlankFieldsModel,
                blank_char_field=lambda: choice_mock(lst)
            )
            r.make().blank_char_field
            r.make().blank_char_field
            assert choice_mock.call_count == 2

    def test_always_calls_with_quantity(self):
        with patch('tests.test_recipes.choice') as choice_mock:
            choice_mock.return_value = 'foo'
            lst = ['foo', 'bar', 'spam', 'eggs']
            r = Recipe(
                DummyBlankFieldsModel,
                blank_char_field=lambda: choice_mock(lst)
            )
            r.make(_quantity=3)
            assert choice_mock.call_count == 3

    def test_make_recipes_with_args(self):
        """
          Overriding some fields values at recipe execution
        """
        person = person_recipe.make(name='Guido', age=56)
        assert person.name != recipe_attrs['name']
        assert person.name == 'Guido'

        assert person.age != recipe_attrs['age']
        assert person.age == 56

        assert person.nickname == recipe_attrs['nickname']
        assert person.bio == recipe_attrs['bio']
        assert person.birthday == recipe_attrs['birthday']
        assert person.appointment == recipe_attrs['appointment']
        assert person.blog == recipe_attrs['blog']
        assert person.wanted_games_qtd == recipe_attrs['wanted_games_qtd']
        assert person.id is not None

    def test_prepare_recipes_with_args(self):
        """
          Overriding some fields values at recipe execution
        """
        person = person_recipe.prepare(name='Guido', age=56)
        assert person.name != recipe_attrs['name']
        assert person.name == 'Guido'

        assert person.age != recipe_attrs['age']
        assert person.age == 56

        assert person.nickname == recipe_attrs['nickname']
        assert person.bio == recipe_attrs['bio']
        assert person.birthday == recipe_attrs['birthday']
        assert person.appointment == recipe_attrs['appointment']
        assert person.blog == recipe_attrs['blog']
        assert person.wanted_games_qtd == recipe_attrs['wanted_games_qtd']
        assert person.id == None

    def test_make_recipe_without_all_model_needed_data(self):
        person_recipe = Recipe(Person, name='John Doe')
        person = person_recipe.make()
        assert 'John Doe' == person.name
        assert person.nickname
        assert person.age
        assert person.bio
        assert person.birthday
        assert person.appointment
        assert person.blog
        assert person.wanted_games_qtd
        assert person.id

    def test_prepare_recipe_without_all_model_needed_data(self):
        person_recipe = Recipe(Person, name='John Doe')
        person = person_recipe.prepare()
        assert 'John Doe' == person.name
        assert person.nickname
        assert person.age
        assert person.bio
        assert person.birthday
        assert person.appointment
        assert person.blog
        assert person.wanted_games_qtd
        assert not person.id

    def test_defining_recipes_str(self):
        from model_mommy.recipe import seq
        p = Recipe(
            'generic.Person',
            name=seq('foo')
        )
        try:
            p.make(_quantity=5)
        except AttributeError as e:
            self.fail('%s' % e)


@pytest.mark.django_db
class TestExecutingRecipes():
    """
      Tests for calling recipes defined in mommy_recipes.py
    """
    def test_model_with_foreign_key(self):
        dog = mommy.make_recipe('tests.generic.dog')
        assert dog.breed == 'Pug'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id

        dog = mommy.prepare_recipe('tests.generic.dog')
        assert dog.breed == 'Pug'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id is None

        dog = mommy.prepare_recipe('tests.generic.dog', _save_related=True)
        assert dog.breed == 'Pug'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id

        dogs = mommy.make_recipe('tests.generic.dog', _quantity=2)
        owner = dogs[0].owner
        for dog in dogs:
            assert dog.breed == 'Pug'
            assert dog.owner == owner

    def test_model_with_foreign_key_as_str(self):
        dog = mommy.make_recipe('tests.generic.other_dog')
        assert dog.breed == 'Basset'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id

        dog = mommy.prepare_recipe('tests.generic.other_dog')
        assert dog.breed == 'Basset'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id is None

    def test_model_with_foreign_key_as_unicode(self):
        dog = mommy.make_recipe('tests.generic.other_dog_unicode')
        assert dog.breed == 'Basset'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id

        dog = mommy.prepare_recipe('tests.generic.other_dog_unicode')
        assert dog.breed == 'Basset'
        assert isinstance(dog.owner, Person)
        assert dog.owner.id is None

    def test_make_recipe(self):
        person = mommy.make_recipe('tests.generic.person')
        assert isinstance(person, Person)
        assert person.id

    def test_make_recipe_with_quantity_parameter(self):
        people = mommy.make_recipe('tests.generic.person', _quantity=3)
        assert len(people) == 3
        for person in people:
            assert isinstance(person, Person)
            assert person.id

    def test_make_extended_recipe(self):
        extended_dog = mommy.make_recipe('tests.generic.extended_dog')
        assert extended_dog.breed == 'Super basset'
        # No side effects happened due to extension
        base_dog = mommy.make_recipe('tests.generic.dog')
        assert base_dog.breed == 'Pug'

    def test_extended_recipe_type(self):
        assert isinstance(pug, SmallDogRecipe)

    def test_save_related_instances_on_prepare_recipe(self):
        dog = mommy.prepare_recipe('tests.generic.homeless_dog')
        assert not dog.id
        assert not dog.owner.id

        dog = mommy.prepare_recipe('tests.generic.homeless_dog', _save_related=True)
        assert not dog.id
        assert dog.owner.id

    def test_make_recipe_with_quantity_parameter_respection_model_args(self):
        people = mommy.make_recipe(
            'tests.generic.person',
            _quantity=3,
            name='Dennis Ritchie',
            age=70
        )
        assert len(people) == 3
        for person in people:
            assert person.name == 'Dennis Ritchie'
            assert person.age == 70

    def test_make_recipe_raises_correct_exception_if_invalid_quantity(self):
        with pytest.raises(InvalidQuantityException):
            mommy.make_recipe('tests.generic.person', _quantity="hi")
        with pytest.raises(InvalidQuantityException):
            mommy.make_recipe('tests.generic.person', _quantity=-1)

    def test_prepare_recipe_with_foreign_key(self):
        person_recipe = Recipe(Person, name='John Doe')
        dog_recipe = Recipe(
            Dog,
            owner=foreign_key(person_recipe),
        )
        dog = dog_recipe.prepare()

        assert dog.id is None
        assert dog.owner.id is None

    def test_prepare_recipe_with_quantity_parameter(self):
        people = mommy.prepare_recipe('tests.generic.person', _quantity=3)
        assert len(people) == 3
        for person in people:
            assert isinstance(person, Person)
            assert person.id == None

    def test_prepare_recipe_with_quantity_parameter_respection_model_args(self):
        people = mommy.prepare_recipe(
            'tests.generic.person',
            _quantity=3,
            name='Dennis Ritchie',
            age=70
        )
        assert len(people) == 3
        for person in people:
            assert person.name == 'Dennis Ritchie'
            assert person.age == 70

    def test_prepare_recipe_raises_correct_exception_if_invalid_quantity(self):
        with pytest.raises(InvalidQuantityException):
            mommy.prepare_recipe('tests.generic.person', _quantity="hi")
        with pytest.raises(InvalidQuantityException):
            mommy.prepare_recipe('tests.generic.person', _quantity=-1)

    def test_prepare_recipe(self):
        person = mommy.prepare_recipe('tests.generic.person')
        assert isinstance(person, Person)
        assert not person.id

    def test_make_recipe_with_args(self):
        person = mommy.make_recipe('tests.generic.person', name='Dennis Ritchie', age=70)
        assert person.name == 'Dennis Ritchie'
        assert person.age == 70

    def test_prepare_recipe_with_args(self):
        person = mommy.prepare_recipe('tests.generic.person', name='Dennis Ritchie', age=70)
        assert person.name == 'Dennis Ritchie'
        assert person.age == 70

    def test_import_recipe_inside_deeper_modules(self):
        recipe_name = 'tests.generic.tests.sub_package.person'
        person = mommy.prepare_recipe(recipe_name)
        assert person.name == 'John Deeper'

    def test_pass_save_kwargs(self):
        owner = mommy.make(Person)

        dog = mommy.make_recipe('tests.generic.overrided_save', _save_kwargs={'owner': owner})
        assert owner == dog.owner


@pytest.mark.django_db
class TestForeignKey():

    def test_foreign_key_method_returns_a_recipe_foreign_key_object(self):
        number_recipe = Recipe(
            DummyNumbersModel,
            float_field=1.6
        )
        obj = foreign_key(number_recipe)
        assert isinstance(obj, RecipeForeignKey)

    def test_not_accept_other_type(self):
        with pytest.raises(TypeError) as c:
            foreign_key(2)
        exception = c.value
        assert str(exception) == 'Not a recipe'

    def test_do_not_create_related_model(self):
        """
          It should not attempt to create other object when
          passing the object as argument
        """
        person = mommy.make_recipe('tests.generic.person')
        assert Person.objects.count() == 1
        mommy.make_recipe('tests.generic.dog', owner=person)
        assert Person.objects.count() == 1
        mommy.prepare_recipe('tests.generic.dog', owner=person)
        assert Person.objects.count() == 1

    def test_do_query_lookup_for_recipes_make_method(self):
        """
          It should not attempt to create other object when
          using query lookup syntax
        """
        dog = mommy.make_recipe('tests.generic.dog', owner__name='James')
        assert Person.objects.count() == 1
        assert dog.owner.name == 'James'

    def test_do_query_lookup_for_recipes_prepare_method(self):
        """
          It should not attempt to create other object when
          using query lookup syntax
        """
        dog = mommy.prepare_recipe('tests.generic.dog', owner__name='James')
        assert dog.owner.name == 'James'

    def test_do_query_lookup_empty_recipes(self):
        """
          It should not attempt to create other object when
          using query lookup syntax
        """
        dog_recipe = Recipe(Dog)
        dog = dog_recipe.make(owner__name='James')
        assert Person.objects.count() == 1
        assert dog.owner.name == 'James'

        dog = dog_recipe.prepare(owner__name='Zezin')
        assert Person.objects.count() == 1
        assert dog.owner.name == 'Zezin'

    def test_related_models_recipes(self):
        lady = mommy.make_recipe('tests.generic.dog_lady')
        assert lady.dog_set.count() == 2
        assert lady.dog_set.all()[0].breed == 'Pug'
        assert lady.dog_set.all()[1].breed == 'Basset'

    def test_nullable_related(self):
        nullable = mommy.make_recipe('tests.generic.nullable_related')
        assert nullable.dummynullfieldsmodel_set.count() == 1

    def test_chained_related(self):
        movie = mommy.make_recipe('tests.generic.movie_with_cast')
        assert movie.cast_members.count() == 2


@pytest.mark.django_db
class TestM2MField():

    def test_create_many_to_many(self):
        dog = mommy.make_recipe('tests.generic.dog_with_friends')
        assert len(dog.friends_with.all()) == 2
        for friend in dog.friends_with.all():
            assert friend.breed == 'Pug'
            assert friend.owner.name == 'John Doe'

    def test_create_nested(self):
        dog = mommy.make_recipe('tests.generic.dog_with_more_friends')
        assert len(dog.friends_with.all()) == 1
        friend = dog.friends_with.all()[0]
        assert len(friend.friends_with.all()) == 2


@pytest.mark.django_db
class TestSequences():

    def test_increment_for_strings(self):
        person = mommy.make_recipe('tests.generic.serial_person')
        assert person.name == 'joe1'
        person = mommy.prepare_recipe('tests.generic.serial_person')
        assert person.name == 'joe2'
        person = mommy.make_recipe('tests.generic.serial_person')
        assert person.name == 'joe3'

    def test_increment_for_numbers(self):
        dummy = mommy.make_recipe('tests.generic.serial_numbers')
        assert dummy.default_int_field == 11
        assert dummy.default_decimal_field == Decimal('21.1')
        assert dummy.default_float_field == 2.23
        dummy = mommy.make_recipe('tests.generic.serial_numbers')
        assert dummy.default_int_field == 12
        assert dummy.default_decimal_field == Decimal('22.1')
        assert dummy.default_float_field == 3.23
        dummy = mommy.prepare_recipe('tests.generic.serial_numbers')
        assert dummy.default_int_field == 13
        assert dummy.default_decimal_field == Decimal('23.1')
        assert dummy.default_float_field == 4.23

    def test_increment_for_numbers_2(self):
        """
        This test is a repeated one but it is necessary to ensure Sequences atomicity
        """
        dummy = mommy.make_recipe('tests.generic.serial_numbers')
        assert dummy.default_int_field == 11
        assert dummy.default_decimal_field == Decimal('21.1')
        assert dummy.default_float_field == 2.23
        dummy = mommy.make_recipe('tests.generic.serial_numbers')
        assert dummy.default_int_field == 12
        assert dummy.default_decimal_field == Decimal('22.1')
        assert dummy.default_float_field == 3.23
        dummy = mommy.prepare_recipe('tests.generic.serial_numbers')
        assert dummy.default_int_field == 13
        assert dummy.default_decimal_field == Decimal('23.1')
        assert dummy.default_float_field == 4.23

    def test_creates_unique_field_recipe_using_for_iterator(self):
        for i in range(1, 4):
            dummy = mommy.make_recipe('tests.generic.dummy_unique_field')
            assert dummy.value == 10 + i

    def test_creates_unique_field_recipe_using_quantity_argument(self):
        dummies = mommy.make_recipe('tests.generic.dummy_unique_field', _quantity=3)
        assert 11 == dummies[0].value
        assert 12 == dummies[1].value
        assert 13 == dummies[2].value

    def test_increment_by_3(self):
        dummy = mommy.make_recipe('tests.generic.serial_numbers_by')
        assert dummy.default_int_field == 13
        assert dummy.default_decimal_field == Decimal('22.5')
        assert dummy.default_float_field == pytest.approx(3.030000)
        dummy = mommy.make_recipe('tests.generic.serial_numbers_by')
        assert dummy.default_int_field == 16
        assert dummy.default_decimal_field == Decimal('24.9')
        assert dummy.default_float_field == pytest.approx(4.83)
        dummy = mommy.prepare_recipe('tests.generic.serial_numbers_by')
        assert dummy.default_int_field == 19
        assert dummy.default_decimal_field == Decimal('27.3')
        assert dummy.default_float_field == pytest.approx(6.63)

    def test_increment_by_timedelta(self):
        dummy = mommy.make_recipe('tests.generic.serial_datetime')
        assert dummy.default_date_field == (TEST_TIME.date() + timedelta(days=1))
        assert dummy.default_date_time_field == tz_aware(TEST_TIME + timedelta(hours=3))
        assert dummy.default_time_field == (TEST_TIME + timedelta(seconds=15)).time()
        dummy = mommy.make_recipe('tests.generic.serial_datetime')
        assert dummy.default_date_field == (TEST_TIME.date() + timedelta(days=2))
        assert dummy.default_date_time_field == tz_aware(TEST_TIME + timedelta(hours=6))
        assert dummy.default_time_field == (TEST_TIME + timedelta(seconds=30)).time()

    def test_creates_unique_timedelta_recipe_using_quantity_argument(self):
        dummies = mommy.make_recipe('tests.generic.serial_datetime', _quantity=3)
        assert dummies[0].default_date_field == TEST_TIME.date() + timedelta(days=1)
        assert dummies[1].default_date_field == TEST_TIME.date() + timedelta(days=2)
        assert dummies[2].default_date_field == TEST_TIME.date() + timedelta(days=3)

    def test_increment_after_override_definition_field(self):
        person = mommy.make_recipe('tests.generic.serial_person', name='tom')
        assert person.name == 'tom'
        person = mommy.make_recipe('tests.generic.serial_person')
        assert person.name == 'joe4'
        person = mommy.prepare_recipe('tests.generic.serial_person')
        assert person.name == 'joe5'


@pytest.mark.django_db
class TestIterators():

    def test_accepts_generators(self):
        r = Recipe(DummyBlankFieldsModel,
                   blank_char_field=itertools.cycle(['a', 'b']))
        assert 'a' == r.make().blank_char_field
        assert 'b' == r.make().blank_char_field
        assert 'a' == r.make().blank_char_field

    def test_accepts_iterators(self):
        r = Recipe(DummyBlankFieldsModel,
                   blank_char_field=iter(['a', 'b', 'c']))
        assert 'a' == r.make().blank_char_field
        assert 'b' == r.make().blank_char_field
        assert 'c' == r.make().blank_char_field

    def test_empty_iterator_exception(self):
        r = Recipe(DummyBlankFieldsModel,
                   blank_char_field=iter(['a', 'b']))
        assert 'a' == r.make().blank_char_field
        assert 'b' == r.make().blank_char_field
        with pytest.raises(RecipeIteratorEmpty):
            r.make()

    def test_only_iterators_not_iteratables_are_iterated(self):
        """Ensure we only iterate explicit iterators.

        Consider "iterable" vs "iterator":

        Something like a string is "iterable", but not an "iterator". We don't
        want to iterate "iterables", only explicit "iterators".

        """
        r = Recipe(DummyBlankFieldsModel,
                   blank_text_field="not an iterator, so don't iterate!")
        assert r.make().blank_text_field == "not an iterator, so don't iterate!"
