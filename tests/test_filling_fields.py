import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from os.path import abspath
from tempfile import gettempdir

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import images, File
from django.db import connection
from django.db.models import fields, ImageField, FileField

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


@pytest.fixture
def person(db):
    return mommy.make('generic.Person')


@pytest.fixture()
def custom_cfg():
    yield None
    if hasattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN'):
        delattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN')
    mommy.generators.add('tests.generic.fields.CustomFieldWithGenerator', None)
    mommy.generators.add('django.db.models.fields.CharField', None)


class TestFillingFromChoice():

    def test_if_gender_is_populated_from_choices(self, person):
        from tests.generic.models import GENDER_CHOICES
        person.gender in map(lambda x: x[0], GENDER_CHOICES)

    def test_if_occupation_populated_from_choices(self, person):
        from tests.generic.models import OCCUPATION_CHOICES
        occupations = [item[0] for list in OCCUPATION_CHOICES for item in list[1]]
        person.occupation in occupations


class TestStringFieldsFilling():

    def test_fill_CharField_with_a_random_str(self, person):
        person_name_field = models.Person._meta.get_field('name')
        assert isinstance(person_name_field, fields.CharField)

        assert isinstance(person.name, str)
        assert len(person.name) == person_name_field.max_length

    def test_fill_SlugField_with_a_random_str(self, person):
        person_nickname_field = models.Person._meta.get_field('nickname')
        assert isinstance(person_nickname_field, fields.SlugField)

        assert isinstance(person.nickname, str)
        assert len(person.nickname) == person_nickname_field.max_length

    def test_fill_TextField_with_a_random_str(self, person):
        person_bio_field = models.Person._meta.get_field('bio')
        assert isinstance(person_bio_field, fields.TextField)

        assert isinstance(person.bio, str)


class TestBinaryFieldsFilling():

    def test_fill_BinaryField_with_random_binary(self, person):
        name_hash_field = models.Person._meta.get_field('name_hash')
        assert isinstance(name_hash_field, fields.BinaryField)
        name_hash = person.name_hash
        assert isinstance(name_hash, bytes)
        assert len(name_hash) == name_hash_field.max_length


class TestsDurationFieldsFilling():

    def test_fill_DurationField_with_random_interval_in_miliseconds(self, person):
        duration_of_sleep_field = models.Person._meta.get_field('duration_of_sleep')
        assert isinstance(duration_of_sleep_field, fields.DurationField)
        duration_of_sleep = person.duration_of_sleep
        assert isinstance(person.duration_of_sleep, timedelta)


class TestBooleanFieldsFilling():

    def test_fill_BooleanField_with_boolean(self, person):
        happy_field = models.Person._meta.get_field('happy')
        assert isinstance(happy_field, fields.BooleanField)

        assert isinstance(person.happy, bool)
        assert person.happy is True

    def test_fill_BooleanField_with_false_if_default_is_false(self, person):
        unhappy_field = models.Person._meta.get_field('unhappy')
        assert isinstance(unhappy_field, fields.BooleanField)

        assert isinstance(person.unhappy, bool)
        assert person.unhappy is False


class TestDateFieldsFilling():

    def test_fill_DateField_with_a_date(self, person):
        birthday_field = models.Person._meta.get_field('birthday')
        assert isinstance(birthday_field, fields.DateField)
        assert isinstance(person.birthday, date)


class TestDateTimeFieldsFilling():

    def test_fill_DateTimeField_with_a_datetime(self, person):
        appointment_field = models.Person._meta.get_field('appointment')
        assert isinstance(appointment_field, fields.DateTimeField)
        assert isinstance(person.appointment, datetime)


class TestTimeFieldsFilling():

    def test_fill_TimeField_with_a_time(self, person):
        birth_time_field = models.Person._meta.get_field('birth_time')
        assert isinstance(birth_time_field, fields.TimeField)
        assert isinstance(person.birth_time, time)


class TestUUIDFieldsFilling():

    def test_fill_UUIDField_with_uuid_object(self, person):
        uuid_field = models.Person._meta.get_field('uuid')
        assert isinstance(uuid_field, fields.UUIDField)
        assert isinstance(person.uuid, uuid.UUID)


@pytest.mark.django_db
class TestFillingIntFields():

    def test_fill_IntegerField_with_a_random_number(self):
        dummy_int_model = mommy.make(models.DummyIntModel)
        int_field = models.DummyIntModel._meta.get_field('int_field')
        assert isinstance(int_field, fields.IntegerField)
        assert isinstance(dummy_int_model.int_field, int)

    def test_fill_BigIntegerField_with_a_random_number(self):
        dummy_int_model = mommy.make(models.DummyIntModel)
        big_int_field = models.DummyIntModel._meta.get_field('big_int_field')
        assert isinstance(big_int_field, fields.BigIntegerField)
        assert isinstance(dummy_int_model.big_int_field, int)

    def test_fill_SmallIntegerField_with_a_random_number(self):
        dummy_int_model = mommy.make(models.DummyIntModel)
        small_int_field = models.DummyIntModel._meta.get_field('small_int_field')
        assert isinstance(small_int_field, fields.SmallIntegerField)
        assert isinstance(dummy_int_model.small_int_field, int)


@pytest.mark.django_db
class TestFillingPositiveIntFields():

    def test_fill_PositiveSmallIntegerField_with_a_random_number(self):
        dummy_positive_int_model = mommy.make(models.DummyPositiveIntModel)
        field = models.DummyPositiveIntModel._meta.get_field('positive_small_int_field')
        positive_small_int_field = field
        assert isinstance(positive_small_int_field, fields.PositiveSmallIntegerField)
        assert isinstance(dummy_positive_int_model.positive_small_int_field, int)
        assert dummy_positive_int_model.positive_small_int_field > 0

    def test_fill_PositiveIntegerField_with_a_random_number(self):
        dummy_positive_int_model = mommy.make(models.DummyPositiveIntModel)
        positive_int_field = models.DummyPositiveIntModel._meta.get_field('positive_int_field')
        assert isinstance(positive_int_field, fields.PositiveIntegerField)
        assert isinstance(dummy_positive_int_model.positive_int_field, int)
        assert dummy_positive_int_model.positive_int_field > 0


@pytest.mark.django_db
class TestFillingOthersNumericFields():

    def test_filling_FloatField_with_a_random_float(self):
        self.dummy_numbers_model = mommy.make(models.DummyNumbersModel)
        float_field = models.DummyNumbersModel._meta.get_field('float_field')
        assert isinstance(float_field, fields.FloatField)
        assert isinstance(self.dummy_numbers_model.float_field, float)

    def test_filling_DecimalField_with_random_decimal(self):
        self.dummy_decimal_model = mommy.make(models.DummyDecimalModel)
        decimal_field = models.DummyDecimalModel._meta.get_field('decimal_field')
        assert isinstance(decimal_field, fields.DecimalField)
        assert isinstance(self.dummy_decimal_model.decimal_field, Decimal)


class TestURLFieldsFilling():

    def test_fill_URLField_with_valid_url(self, person):
        blog_field = models.Person._meta.get_field('blog')
        assert isinstance(blog_field, fields.URLField)
        assert isinstance(person.blog, str)


class TestFillingEmailField():

    def test_filling_EmailField(self, person):
        field = models.Person._meta.get_field('email')
        assert isinstance(field, fields.EmailField)
        assert isinstance(person.email, str)


@pytest.mark.django_db
class TestFillingIPAddressField():

    def test_filling_IPAddressField(self):
        obj = mommy.make(models.DummyGenericIPAddressFieldModel)
        field = models.DummyGenericIPAddressFieldModel._meta.get_field('ipv4_field')
        assert isinstance(field, fields.GenericIPAddressField)
        assert isinstance(obj.ipv4_field, str)

        validate_ipv4_address(obj.ipv4_field)

        if hasattr(obj, 'ipv6_field'):
            assert isinstance(obj.ipv6_field, str)
            assert isinstance(obj.ipv46_field, str)

            validate_ipv6_address(obj.ipv6_field)
            validate_ipv46_address(obj.ipv46_field)


@pytest.mark.django_db
class TestFillingGenericForeignKeyField():

    def test_filling_content_type_field(self):
        dummy = mommy.make(models.DummyGenericForeignKeyModel)
        assert isinstance(dummy.content_type, ContentType)
        assert dummy.content_type.model_class() is not None


@pytest.mark.django_db
class TestsFillingFileField():

    def test_filling_file_field(self):
        dummy = mommy.make(models.DummyFileFieldModel, _create_files=True)
        field = models.DummyFileFieldModel._meta.get_field('file_field')
        assert isinstance(field, FileField)
        import time
        path = "%s/%s/mock_file.txt" % (gettempdir(), time.strftime('%Y/%m/%d'))

        assert abspath(path) == abspath(dummy.file_field.path)
        dummy.file_field.delete()

    def test_does_not_create_file_if_not_flagged(self):
        dummy = mommy.make(models.DummyFileFieldModel)
        with pytest.raises(ValueError):
            dummy.file_field.path  # Django raises ValueError if file does not exist


@pytest.mark.django_db
class TestFillingCustomFields():

    def test_raises_unsupported_field_for_custom_field(self, custom_cfg):
        """Should raise an exception if a generator is not provided for a custom field"""
        with pytest.raises(TypeError):
            mommy.make(models.CustomFieldWithoutGeneratorModel)

    def test_uses_generator_defined_on_settings_for_custom_field(self, custom_cfg):
        """Should use the function defined in settings as a generator"""
        generator_dict = {'tests.generic.fields.CustomFieldWithGenerator': generators.gen_value_string}
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(models.CustomFieldWithGeneratorModel)
        assert "value" == obj.custom_value

    def test_uses_generator_defined_as_string_on_settings_for_custom_field(self, custom_cfg):
        """Should import and use the function present in the import path defined in settings"""
        generator_dict = {
            'tests.generic.fields.CustomFieldWithGenerator':
                'tests.generic.generators.gen_value_string'
        }
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(models.CustomFieldWithGeneratorModel)
        assert "value" == obj.custom_value

    def test_uses_generator_defined_on_settings_for_custom_foreignkey(self, custom_cfg):
        """Should use the function defined in the import path for a foreign key field"""
        generator_dict = {
            'tests.generic.fields.CustomForeignKey': 'model_mommy.random_gen.gen_related'
        }
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(models.CustomForeignKeyWithGeneratorModel, custom_fk__email="a@b.com")
        assert 'a@b.com' == obj.custom_fk.email

    def test_uses_generator_defined_as_string_for_custom_field(self, custom_cfg):
        """Should import and use the generator function used in the add method"""
        mommy.generators.add(
            'tests.generic.fields.CustomFieldWithGenerator',
            'tests.generic.generators.gen_value_string'
        )
        obj = mommy.make(models.CustomFieldWithGeneratorModel)
        assert "value" == obj.custom_value

    def test_uses_generator_function_for_custom_foreignkey(self, custom_cfg):
        """Should use the generator function passed as a value for the add method"""
        mommy.generators.add('tests.generic.fields.CustomForeignKey', gen_related)
        obj = mommy.make(models.CustomForeignKeyWithGeneratorModel, custom_fk__email="a@b.com")
        assert 'a@b.com' == obj.custom_fk.email

    def test_can_override_django_default_field_functions_generator(self, custom_cfg):
        def gen_char():
            return 'Some value'

        mommy.generators.add('django.db.models.fields.CharField', gen_char)

        person = mommy.make(models.Person)

        assert 'Some value' == person.name


@pytest.mark.django_db
class TestFillingAutoFields():

    def test_filling_AutoField(self):
        obj = mommy.make(models.DummyEmptyModel)
        field = models.DummyEmptyModel._meta.get_field('id')
        assert isinstance(field, fields.AutoField)
        assert isinstance(obj.id, int)


@pytest.mark.django_db
@pytest.mark.skipif(not models.has_pil, reason="PIL is required to test ImageField")
class TestFillingImageFileField():

    def test_filling_image_file_field(self):
        dummy = mommy.make(models.DummyImageFieldModel, _create_files=True)
        field = models.DummyImageFieldModel._meta.get_field('image_field')
        assert isinstance(field, ImageField)
        import time
        path = "%s/%s/mock-img.jpeg" % (gettempdir(), time.strftime('%Y/%m/%d'))

        # These require the file to exist in earlier versions of Django
        assert abspath(path) == abspath(dummy.image_field.path)
        assert dummy.image_field.width
        assert dummy.image_field.height
        dummy.image_field.delete()

    def test_does_not_create_file_if_not_flagged(self):
        dummy = mommy.make(models.DummyImageFieldModel)
        with pytest.raises(ValueError):
            dummy.image_field.path  # Django raises ValueError if file does not exist


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


@pytest.mark.skipif(connection.vendor != 'postgresql', reason='PostgreSQL specific tests')
class TestPostgreSQLFieldsFilling:
    def test_fill_arrayfield_with_empty_array(self, person):
        assert person.acquaintances == []

    def test_fill_jsonfield_with_empty_dict(self, person):
        assert person.data == {}

    def test_fill_hstorefield_with_empty_dict(self, person):
        assert person.hstore_data == {}


@pytest.mark.skipif(not MOMMY_GIS, reason="GIS support required for GIS fields")
class TestGisFieldsFilling():

    def assertGeomValid(self, geom):
        assert geom.valid is True, geom.valid_reason

    def test_fill_PointField_valid(self, person):
        print(MOMMY_GIS)
        self.assertGeomValid(person.point)

    def test_fill_LineStringField_valid(self, person):
        self.assertGeomValid(person.line_string)

    def test_fill_PolygonField_valid(self, person):
        self.assertGeomValid(person.polygon)

    def test_fill_MultiPointField_valid(self, person):
        self.assertGeomValid(person.multi_point)

    def test_fill_MultiLineStringField_valid(self, person):
        self.assertGeomValid(person.multi_line_string)

    def test_fill_MultiPolygonField_valid(self, person):
        self.assertGeomValid(person.multi_polygon)

    def test_fill_GeometryField_valid(self, person):
        self.assertGeomValid(person.geom)

    def test_fill_GeometryCollectionField_valid(self, person):
        self.assertGeomValid(person.geom_collection)
