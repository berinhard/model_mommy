import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from os.path import abspath
from tempfile import gettempdir
from unittest import skipUnless

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import images, File
from django.db import connection
from django.db.models import fields, ImageField, FileField
from django.test import TestCase

from model_mommy import mommy
from model_mommy.gis import MOMMY_GIS
from model_mommy.random_gen import gen_related
from tests.generic import generators, models


try:
    from django.contrib.postgres.fields import (
        ArrayField, CICharField, CIEmailField, CITextField, HStoreField, JSONField,
    )
except ImportError:
    ArrayField = None
    JSONField = None
    HStoreField = None
    CICharField = None
    CIEmailField = None
    CITextField = None

from django.core.validators import (
    validate_ipv4_address, validate_ipv6_address, validate_ipv46_address
)


def assert_not_raise(method, parameters, exception):
    try:
        method(*parameters)
    except exception:
        msg = "Exception %s not expected to be raised" % exception.__name__
        raise AssertionError(msg)


@pytest.fixture
def person(db):
    return mommy.make('generic.Person')


class FieldFillingTestCase(TestCase):

    def setUp(self):
        self.person = mommy.make(models.Person)


class FillingFromChoice(FieldFillingTestCase):

    def test_if_gender_is_populated_from_choices(self):
        from tests.generic.models import GENDER_CH
        self.assertTrue(self.person.gender in map(lambda x: x[0], GENDER_CH))

    def test_if_oppucation_populated_from_choices(self):
        from tests.generic.models import OCCUPATION_CHOCIES
        occupations = [item[0] for list in OCCUPATION_CHOCIES for item in list[1]]
        self.assertTrue(self.person.occupation in occupations)


class StringFieldsFilling(FieldFillingTestCase):

    def test_fill_CharField_with_a_random_str(self):
        person_name_field = models.Person._meta.get_field('name')
        self.assertIsInstance(person_name_field, fields.CharField)

        self.assertIsInstance(self.person.name, str)
        self.assertEqual(len(self.person.name), person_name_field.max_length)

    def test_fill_SlugField_with_a_random_str(self):
        person_nickname_field = models.Person._meta.get_field('nickname')
        self.assertIsInstance(person_nickname_field, fields.SlugField)

        self.assertIsInstance(self.person.nickname, str)
        self.assertEqual(len(self.person.nickname),
                         person_nickname_field.max_length)

    def test_fill_TextField_with_a_random_str(self):
        person_bio_field = models.Person._meta.get_field('bio')
        self.assertIsInstance(person_bio_field, fields.TextField)

        self.assertIsInstance(self.person.bio, str)


@pytest.mark.skipif(connection.vendor != 'postgresql', reason='PostgreSQL specific tests')
class TestCIStringFieldsFilling:
    def test_fill_cicharfield_with_a_random_str(self, person):
        ci_char_field = models.Person._meta.get_field('ci_char')
        assert isinstance(ci_char_field, CICharField)
        assert isinstance(person.ci_char, str)
        assert len(person.ci_char) == ci_char_field.max_length

    def test_filling_ciemailfield(self, person):
        ci_email_field = models.Person._meta.get_field('ci_email')
        assert isinstance(ci_email_field, CIEmailField)
        assert isinstance(person.ci_email, str)

    def test_filling_citextfield(self, person):
        ci_text_field = models.Person._meta.get_field('ci_text')
        assert isinstance(ci_text_field, CITextField)
        assert isinstance(person.ci_text, str)


class BinaryFieldsFilling(FieldFillingTestCase):
    def test_fill_BinaryField_with_random_binary(self):
        name_hash_field = models.Person._meta.get_field('name_hash')
        self.assertIsInstance(name_hash_field, fields.BinaryField)
        name_hash = self.person.name_hash
        self.assertIsInstance(name_hash, bytes)
        self.assertEqual(len(name_hash), name_hash_field.max_length)


class DurationFieldsFilling(FieldFillingTestCase):
    def test_fill_DurationField_with_random_interval_in_miliseconds(self):
        duration_of_sleep_field = models.Person._meta.get_field('duration_of_sleep')
        self.assertIsInstance(duration_of_sleep_field, fields.DurationField)
        duration_of_sleep = self.person.duration_of_sleep
        self.assertIsInstance(duration_of_sleep, timedelta)


class BooleanFieldsFilling(FieldFillingTestCase):
    def test_fill_BooleanField_with_boolean(self):
        happy_field = models.Person._meta.get_field('happy')
        self.assertIsInstance(happy_field, fields.BooleanField)

        self.assertIsInstance(self.person.happy, bool)
        self.assertTrue(self.person.happy)

    def test_fill_BooleanField_with_false_if_default_is_false(self):
        unhappy_field = models.Person._meta.get_field('unhappy')
        self.assertIsInstance(unhappy_field, fields.BooleanField)

        self.assertIsInstance(self.person.unhappy, bool)
        self.assertFalse(self.person.unhappy)


class DateFieldsFilling(FieldFillingTestCase):

    def test_fill_DateField_with_a_date(self):
        birthday_field = models.Person._meta.get_field('birthday')
        self.assertIsInstance(birthday_field, fields.DateField)
        self.assertIsInstance(self.person.birthday, date)


class DateTimeFieldsFilling(FieldFillingTestCase):

    def test_fill_DateTimeField_with_a_datetime(self):
        appointment_field = models.Person._meta.get_field('appointment')
        self.assertIsInstance(appointment_field, fields.DateTimeField)
        self.assertIsInstance(self.person.appointment, datetime)


class TimeFieldsFilling(FieldFillingTestCase):

    def test_fill_TimeField_with_a_time(self):
        birth_time_field = models.Person._meta.get_field('birth_time')
        self.assertIsInstance(birth_time_field, fields.TimeField)
        self.assertIsInstance(self.person.birth_time, time)


class UUIDFieldsFilling(FieldFillingTestCase):
    def test_fill_UUIDField_with_uuid_object(self):
        uuid_field = models.Person._meta.get_field('uuid')
        self.assertIsInstance(uuid_field, fields.UUIDField)

        self.assertIsInstance(self.person.uuid, uuid.UUID)


@pytest.mark.skipif(connection.vendor != 'postgresql', reason='PostgreSQL specific tests')
class TestPostgreSQLFieldsFilling:
    def test_fill_arrayfield_with_empty_array(self, person):
        assert person.acquaintances == []

    def test_fill_jsonfield_with_empty_dict(self, person):
        assert person.data == {}

    def test_fill_hstorefield_with_empty_dict(self, person):
        assert person.hstore_data == {}


class FillingIntFields(TestCase):

    def setUp(self):
        self.dummy_int_model = mommy.make(models.DummyIntModel)

    def test_fill_IntegerField_with_a_random_number(self):
        int_field = models.DummyIntModel._meta.get_field('int_field')
        self.assertIsInstance(int_field, fields.IntegerField)
        self.assertIsInstance(self.dummy_int_model.int_field, int)

    def test_fill_BigIntegerField_with_a_random_number(self):
        big_int_field = models.DummyIntModel._meta.get_field('big_int_field')
        self.assertIsInstance(big_int_field, fields.BigIntegerField)
        self.assertIsInstance(self.dummy_int_model.big_int_field, int)

    def test_fill_SmallIntegerField_with_a_random_number(self):
        small_int_field = models.DummyIntModel._meta.get_field('small_int_field')
        self.assertIsInstance(small_int_field, fields.SmallIntegerField)
        self.assertIsInstance(self.dummy_int_model.small_int_field, int)


class FillingPositiveIntFields(TestCase):

    def setUp(self):
        self.dummy_positive_int_model = mommy.make(models.DummyPositiveIntModel)

    def test_fill_PositiveSmallIntegerField_with_a_random_number(self):
        field = models.DummyPositiveIntModel._meta.get_field('positive_small_int_field')
        positive_small_int_field = field
        self.assertIsInstance(positive_small_int_field, fields.PositiveSmallIntegerField)
        self.assertIsInstance(self.dummy_positive_int_model.positive_small_int_field, int)
        self.assertTrue(self.dummy_positive_int_model.positive_small_int_field > 0)

    def test_fill_PositiveIntegerField_with_a_random_number(self):
        positive_int_field = models.DummyPositiveIntModel._meta.get_field('positive_int_field')
        self.assertIsInstance(positive_int_field, fields.PositiveIntegerField)
        self.assertIsInstance(self.dummy_positive_int_model.positive_int_field, int)
        self.assertTrue(self.dummy_positive_int_model.positive_int_field > 0)


class FillingOthersNumericFields(TestCase):
    def test_filling_FloatField_with_a_random_float(self):
        self.dummy_numbers_model = mommy.make(models.DummyNumbersModel)
        float_field = models.DummyNumbersModel._meta.get_field('float_field')
        self.assertIsInstance(float_field, fields.FloatField)
        self.assertIsInstance(self.dummy_numbers_model.float_field, float)

    def test_filling_DecimalField_with_random_decimal(self):
        self.dummy_decimal_model = mommy.make(models.DummyDecimalModel)
        decimal_field = models.DummyDecimalModel._meta.get_field('decimal_field')
        self.assertIsInstance(decimal_field, fields.DecimalField)
        self.assertIsInstance(self.dummy_decimal_model.decimal_field, Decimal)


class URLFieldsFilling(FieldFillingTestCase):

    def test_fill_URLField_with_valid_url(self):
        blog_field = models.Person._meta.get_field('blog')
        self.assertIsInstance(blog_field, fields.URLField)
        self.assertIsInstance(self.person.blog, str)


class FillingEmailField(TestCase):

    def test_filling_EmailField(self):
        obj = mommy.make(models.DummyEmailModel)
        field = models.DummyEmailModel._meta.get_field('email_field')
        self.assertIsInstance(field, fields.EmailField)
        self.assertIsInstance(obj.email_field, str)


class FillingIPAddressField(TestCase):

    def test_filling_IPAddressField(self):
        obj = mommy.make(models.DummyGenericIPAddressFieldModel)
        field = models.DummyGenericIPAddressFieldModel._meta.get_field('ipv4_field')
        self.assertIsInstance(field, fields.GenericIPAddressField)
        self.assertIsInstance(obj.ipv4_field, str)

        validate_ipv4_address(obj.ipv4_field)

        if hasattr(obj, 'ipv6_field'):
            self.assertIsInstance(obj.ipv6_field, str)
            self.assertIsInstance(obj.ipv46_field, str)

            validate_ipv6_address(obj.ipv6_field)
            validate_ipv46_address(obj.ipv46_field)


class FillingGenericForeignKeyField(TestCase):

    def test_filling_content_type_field(self):
        dummy = mommy.make(models.DummyGenericForeignKeyModel)
        self.assertIsInstance(dummy.content_type, ContentType)
        self.assertIsNotNone(dummy.content_type.model_class())


class FillingFileField(TestCase):

    def setUp(self):
        path = mommy.mock_file_txt
        self.fixture_txt_file = File(open(path))

    def tearDown(self):
        self.dummy.file_field.delete()

    def test_filling_file_field(self):
        self.dummy = mommy.make(models.DummyFileFieldModel, _create_files=True)
        field = models.DummyFileFieldModel._meta.get_field('file_field')
        self.assertIsInstance(field, FileField)
        import time
        path = "%s/%s/mock_file.txt" % (gettempdir(), time.strftime('%Y/%m/%d'))

        self.assertEqual(abspath(self.dummy.file_field.path), abspath(path))

    def test_does_not_create_file_if_not_flagged(self):
        self.dummy = mommy.make(models.DummyFileFieldModel)
        with self.assertRaises(ValueError):
            self.dummy.file_field.path  # Django raises ValueError if file does not exist


@skipUnless(models.has_pil, "PIL is required to test ImageField")
class FillingImageFileField(TestCase):

    def setUp(self):
        path = mommy.mock_file_jpeg
        self.fixture_img_file = images.ImageFile(open(path))

    def tearDown(self):
        self.dummy.image_field.delete()

    def test_filling_image_file_field(self):
        self.dummy = mommy.make(models.DummyImageFieldModel, _create_files=True)
        field = models.DummyImageFieldModel._meta.get_field('image_field')
        self.assertIsInstance(field, ImageField)
        import time
        path = "%s/%s/mock-img.jpeg" % (gettempdir(), time.strftime('%Y/%m/%d'))

        # These require the file to exist in earlier versions of Django
        self.assertEqual(abspath(self.dummy.image_field.path), abspath(path))
        self.assertTrue(self.dummy.image_field.width)
        self.assertTrue(self.dummy.image_field.height)

    def test_does_not_create_file_if_not_flagged(self):
        self.dummy = mommy.make(models.DummyImageFieldModel)
        with self.assertRaises(ValueError):
            self.dummy.image_field.path  # Django raises ValueError if file does not exist


class FillingCustomFields(TestCase):

    def tearDown(self):
        if hasattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN'):
            delattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN')
        mommy.generators.add('tests.generic.fields.CustomFieldWithGenerator', None)
        mommy.generators.add('django.db.models.fields.CharField', None)

    def test_raises_unsupported_field_for_custom_field(self):
        """Should raise an exception if a generator is not provided for a custom field"""
        self.assertRaises(TypeError, mommy.make, models.CustomFieldWithoutGeneratorModel)

    def test_uses_generator_defined_on_settings_for_custom_field(self):
        """Should use the function defined in settings as a generator"""
        generator_dict = {'tests.generic.fields.CustomFieldWithGenerator': generators.gen_value_string}
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(models.CustomFieldWithGeneratorModel)
        self.assertEqual("value", obj.custom_value)

    def test_uses_generator_defined_as_string_on_settings_for_custom_field(self):
        """Should import and use the function present in the import path defined in settings"""
        generator_dict = {
            'tests.generic.fields.CustomFieldWithGenerator':
                'tests.generic.generators.gen_value_string'
        }
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(models.CustomFieldWithGeneratorModel)
        self.assertEqual("value", obj.custom_value)

    def test_uses_generator_defined_on_settings_for_custom_foreignkey(self):
        """Should use the function defined in the import path for a foreign key field"""
        generator_dict = {
            'tests.generic.fields.CustomForeignKey': 'model_mommy.random_gen.gen_related'
        }
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(models.CustomForeignKeyWithGeneratorModel, custom_fk__email="a@b.com")
        self.assertEqual('a@b.com', obj.custom_fk.email)

    def test_uses_generator_defined_as_string_for_custom_field(self):
        """Should import and use the generator function used in the add method"""
        mommy.generators.add(
            'tests.generic.fields.CustomFieldWithGenerator',
            'tests.generic.generators.gen_value_string'
        )
        obj = mommy.make(models.CustomFieldWithGeneratorModel)
        self.assertEqual("value", obj.custom_value)

    def test_uses_generator_function_for_custom_foreignkey(self):
        """Should use the generator function passed as a value for the add method"""
        mommy.generators.add('tests.generic.fields.CustomForeignKey', gen_related)
        obj = mommy.make(models.CustomForeignKeyWithGeneratorModel, custom_fk__email="a@b.com")
        self.assertEqual('a@b.com', obj.custom_fk.email)

    def test_can_override_django_default_field_functions_generator(self):
        def gen_char():
            return 'Some value'

        mommy.generators.add('django.db.models.fields.CharField', gen_char)

        person = mommy.make(models.Person)

        self.assertEqual('Some value', person.name)


class FillingAutoFields(TestCase):

    def test_filling_AutoField(self):
        obj = mommy.make(models.DummyEmptyModel)
        field = models.DummyEmptyModel._meta.get_field('id')
        self.assertIsInstance(field, fields.AutoField)
        self.assertIsInstance(obj.id, int)


@skipUnless(MOMMY_GIS, "GIS support required for GIS fields")
class GisFieldsFilling(FieldFillingTestCase):

    def assertGeomValid(self, geom):
        self.assertTrue(geom.valid, geom.valid_reason)

    def test_fill_PointField_valid(self):
        self.assertGeomValid(self.person.point)

    def test_fill_LineStringField_valid(self):
        self.assertGeomValid(self.person.line_string)

    def test_fill_PolygonField_valid(self):
        self.assertGeomValid(self.person.polygon)

    def test_fill_MultiPointField_valid(self):
        self.assertGeomValid(self.person.multi_point)

    def test_fill_MultiLineStringField_valid(self):
        self.assertGeomValid(self.person.multi_line_string)

    def test_fill_MultiPolygonField_valid(self):
        self.assertGeomValid(self.person.multi_polygon)

    def test_fill_GeometryField_valid(self):
        self.assertGeomValid(self.person.geom)

    def test_fill_GeometryCollectionField_valid(self):
        self.assertGeomValid(self.person.geom_collection)
