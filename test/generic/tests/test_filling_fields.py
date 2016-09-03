from datetime import date, datetime, time, timedelta
from decimal import Decimal
from os.path import abspath
from tempfile import gettempdir

from django.test import TestCase
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import CharField, TextField, SlugField
from django.db.models.fields import DateField, DateTimeField,TimeField, EmailField
from django.db.models.fields import IPAddressField, AutoField
try:
    from django.db.models.fields import GenericIPAddressField
except ImportError:
    GenericIPAddressField = IPAddressField
from django.db.models.fields import IntegerField, SmallIntegerField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields import FloatField, DecimalField
from django.db.models.fields import BooleanField, URLField
from django.db.models import FileField, ImageField
from django.core.files import File
from django.core.files.images import ImageFile

try:
    from django.db.models.fields import BigIntegerField
except ImportError:
    pass
    #BigIntegerField = IntegerField

from six import text_type, string_types, binary_type

from model_mommy import mommy
from test.generic.models import has_pil
from test.generic.models import Person
from test.generic.models import DummyIntModel, DummyPositiveIntModel
from test.generic.models import DummyNumbersModel, DummyEmptyModel
from test.generic.models import DummyDecimalModel, DummyEmailModel
from test.generic.models import DummyGenericForeignKeyModel
from test.generic.models import DummyFileFieldModel
from test.generic.models import DummyImageFieldModel
from test.generic.models import CustomFieldWithoutGeneratorModel, CustomFieldWithGeneratorModel
from test.generic.models import CustomForeignKeyWithGeneratorModel
from test.generic.generators import gen_value_string

try:
    from django.db.models.fields import BinaryField
except ImportError:
    BinaryField = None

try:
    from django.db.models.fields import DurationField
except ImportError:
    DurationField = None

try:
    from django.db.models.fields import UUIDField
except ImportError:
    UUIDField = None

try:
    from django.contrib.postgres.fields import ArrayField
except ImportError:
    ArrayField = None

try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    JSONField = None

from django.core.validators import validate_ipv4_address
try:
    from django.core.validators import validate_ipv6_address, validate_ipv46_address
except ImportError:
    def validate_ipv6_address(v):
        raise ValidationError()
    validate_ipv46_address = validate_ipv6_address


__all__ = [
    'StringFieldsFilling', 'BooleanFieldsFilling', 'DateTimeFieldsFilling',
    'DateFieldsFilling', 'FillingIntFields', 'FillingPositiveIntFields',
    'FillingOthersNumericFields', 'FillingFromChoice', 'URLFieldsFilling',
    'FillingEmailField', 'FillingIPAddressField', 'FillingGenericForeignKeyField', 'FillingFileField',
    'FillingImageFileField', 'TimeFieldsFilling', 'FillingCustomFields',
]

if BinaryField:
    __all__.append('BinaryFieldsFilling')

if DurationField:
    __all__.append('DurationField')


def assert_not_raise(method, parameters, exception):
    try:
        method(*parameters)
    except exception:
        msg = "Exception %s not expected to be raised" % exception.__name__
        raise AssertionError(msg)


class FieldFillingTestCase(TestCase):

    def setUp(self):
        self.person = mommy.make(Person)


class FillingFromChoice(FieldFillingTestCase):

    def test_if_gender_is_populated_from_choices(self):
        from test.generic.models import GENDER_CH
        self.assertTrue(self.person.gender in map(lambda x: x[0], GENDER_CH))

    def test_if_oppucation_populated_from_choices(self):
        from test.generic.models import OCCUPATION_CHOCIES
        occupations = [item[0] for list in OCCUPATION_CHOCIES for item in list[1]]
        self.assertTrue(self.person.occupation in occupations)


class StringFieldsFilling(FieldFillingTestCase):

    def test_fill_CharField_with_a_random_str(self):
        person_name_field = Person._meta.get_field('name')
        self.assertIsInstance(person_name_field, CharField)

        self.assertIsInstance(self.person.name, text_type)
        self.assertEqual(len(self.person.name), person_name_field.max_length)

    def test_fill_SlugField_with_a_random_str(self):
        person_nickname_field = Person._meta.get_field('nickname')
        self.assertIsInstance(person_nickname_field, SlugField)

        self.assertIsInstance(self.person.nickname, text_type)
        self.assertEqual(len(self.person.nickname),
                         person_nickname_field.max_length)

    def test_fill_TextField_with_a_random_str(self):
        person_bio_field = Person._meta.get_field('bio')
        self.assertIsInstance(person_bio_field, TextField)

        self.assertIsInstance(self.person.bio, text_type)


class BinaryFieldsFilling(FieldFillingTestCase):
    if BinaryField:
        def test_fill_BinaryField_with_random_binary(self):
            name_hash_field = Person._meta.get_field('name_hash')
            self.assertIsInstance(name_hash_field, BinaryField)
            name_hash = self.person.name_hash
            self.assertIsInstance(name_hash, binary_type)
            self.assertEqual(len(name_hash), name_hash_field.max_length)


class DurationFieldsFilling(FieldFillingTestCase):
    if DurationField:
        def test_fill_DurationField_with_random_interval_in_miliseconds(self):
            duration_of_sleep_field = Person._meta.get_field('duration_of_sleep')
            self.assertIsInstance(duration_of_sleep_field, DurationField)
            duration_of_sleep = self.person.duration_of_sleep
            self.assertIsInstance(duration_of_sleep, timedelta)


class BooleanFieldsFilling(FieldFillingTestCase):
    def test_fill_BooleanField_with_boolean(self):
        happy_field = Person._meta.get_field('happy')
        self.assertIsInstance(happy_field, BooleanField)

        self.assertIsInstance(self.person.happy, bool)
        self.assertTrue(self.person.happy)

    def test_fill_BooleanField_with_false_if_default_is_false(self):
        unhappy_field = Person._meta.get_field('unhappy')
        self.assertIsInstance(unhappy_field, BooleanField)

        self.assertIsInstance(self.person.unhappy, bool)
        self.assertFalse(self.person.unhappy)


class DateFieldsFilling(FieldFillingTestCase):

    def test_fill_DateField_with_a_date(self):
        birthday_field = Person._meta.get_field('birthday')
        self.assertIsInstance(birthday_field, DateField)

        self.assertIsInstance(self.person.birthday, date)


class DateTimeFieldsFilling(FieldFillingTestCase):

    def test_fill_DateTimeField_with_a_datetime(self):
        appointment_field = Person._meta.get_field('appointment')
        self.assertIsInstance(appointment_field, DateTimeField)

        self.assertIsInstance(self.person.appointment, datetime)


class TimeFieldsFilling(FieldFillingTestCase):

    def test_fill_TimeField_with_a_time(self):
        birth_time_field = Person._meta.get_field('birth_time')
        self.assertIsInstance(birth_time_field, TimeField)

        self.assertIsInstance(self.person.birth_time, time)


class UUIDFieldsFilling(FieldFillingTestCase):

    if UUIDField:
        def test_fill_UUIDField_with_uuid_object(self):
            import uuid

            uuid_field = Person._meta.get_field('uuid')
            self.assertIsInstance(uuid_field, UUIDField)

            self.assertIsInstance(self.person.uuid, uuid.UUID)


class ArrayFieldsFilling(FieldFillingTestCase):

    if ArrayField:
        def test_fill_ArrayField_with_uuid_object(self):
            self.assertEqual(self.person.acquaintances, [])


class JSONFieldsFilling(FieldFillingTestCase):

    if JSONField:
        def test_fill_ArrayField_with_uuid_object(self):
            self.assertEqual(self.person.data, {})

class FillingIntFields(TestCase):

    def setUp(self):
        self.dummy_int_model = mommy.make(DummyIntModel)

    def test_fill_IntegerField_with_a_random_number(self):
        int_field = DummyIntModel._meta.get_field('int_field')
        self.assertIsInstance(int_field, IntegerField)

        self.assertIsInstance(self.dummy_int_model.int_field, int)

    def test_fill_BigIntegerField_with_a_random_number(self):
        big_int_field = DummyIntModel._meta.get_field('big_int_field')
        self.assertIsInstance(big_int_field, BigIntegerField)

        self.assertIsInstance(self.dummy_int_model.big_int_field, int)

    def test_fill_SmallIntegerField_with_a_random_number(self):

        small_int_field = DummyIntModel._meta.get_field('small_int_field')
        self.assertIsInstance(small_int_field, SmallIntegerField)

        self.assertIsInstance(self.dummy_int_model.small_int_field, int)


class FillingPositiveIntFields(TestCase):

    def setUp(self):
        self.dummy_positive_int_model = mommy.make(DummyPositiveIntModel)

    def test_fill_PositiveSmallIntegerField_with_a_random_number(self):
        field = DummyPositiveIntModel._meta.get_field('positive_small_int_field')
        positive_small_int_field = field
        self.assertIsInstance(positive_small_int_field, PositiveSmallIntegerField)

        self.assertIsInstance(self.dummy_positive_int_model.positive_small_int_field, int)
        self.assertTrue(self.dummy_positive_int_model.positive_small_int_field > 0)

    def test_fill_PositiveIntegerField_with_a_random_number(self):
        positive_int_field = DummyPositiveIntModel._meta.get_field('positive_int_field')
        self.assertIsInstance(positive_int_field, PositiveIntegerField)

        self.assertIsInstance(self.dummy_positive_int_model.positive_int_field, int)
        self.assertTrue(self.dummy_positive_int_model.positive_int_field > 0)


class FillingOthersNumericFields(TestCase):
    def test_filling_FloatField_with_a_random_float(self):
        self.dummy_numbers_model = mommy.make(DummyNumbersModel)
        float_field = DummyNumbersModel._meta.get_field('float_field')
        self.assertIsInstance(float_field, FloatField)
        self.assertIsInstance(self.dummy_numbers_model.float_field, float)

    def test_filling_DecimalField_with_random_decimal(self):
        self.dummy_decimal_model = mommy.make(DummyDecimalModel)
        decimal_field = DummyDecimalModel._meta.get_field('decimal_field')

        self.assertIsInstance(decimal_field, DecimalField)
        self.assertIsInstance(self.dummy_decimal_model.decimal_field, Decimal)


class URLFieldsFilling(FieldFillingTestCase):

    def test_fill_URLField_with_valid_url(self):
        blog_field = Person._meta.get_field('blog')
        self.assertIsInstance(blog_field, URLField)

        self.assertIsInstance(self.person.blog, text_type)


class FillingEmailField(TestCase):

    def test_filling_EmailField(self):
        obj = mommy.make(DummyEmailModel)
        field = DummyEmailModel._meta.get_field('email_field')
        self.assertIsInstance(field, EmailField)
        self.assertIsInstance(obj.email_field, string_types)


class FillingIPAddressField(TestCase):

    def test_filling_IPAddressField(self):
        try:
            from test.generic.models import DummyGenericIPAddressFieldModel as IPModel
        except ImportError:
            from test.generic.models import DummyIPAddressFieldModel as IPModel

        obj = mommy.make(IPModel)
        field = IPModel._meta.get_field('ipv4_field')
        self.assertIsInstance(field, GenericIPAddressField)
        self.assertIsInstance(obj.ipv4_field, string_types)

        validate_ipv4_address(obj.ipv4_field)

        if hasattr(obj, 'ipv6_field'):
            self.assertIsInstance(obj.ipv6_field, string_types)
            self.assertIsInstance(obj.ipv46_field, string_types)

            validate_ipv6_address(obj.ipv6_field)
            validate_ipv46_address(obj.ipv46_field)


class FillingGenericForeignKeyField(TestCase):

    def test_filling_content_type_field(self):
        dummy = mommy.make(DummyGenericForeignKeyModel)
        self.assertIsInstance(dummy.content_type, ContentType)
        self.assertIsNotNone(dummy.content_type.model_class())


class FillingFileField(TestCase):

    def setUp(self):
        path = mommy.mock_file_txt
        self.fixture_txt_file = File(open(path))

    def test_filling_file_field(self):
        self.dummy = mommy.make(DummyFileFieldModel)
        field = DummyFileFieldModel._meta.get_field('file_field')
        self.assertIsInstance(field, FileField)
        import time
        path = "%s/%s/mock_file.txt" % (gettempdir(), time.strftime('%Y/%m/%d'))

        from django import VERSION
        if VERSION[1] >= 4:
            self.assertEqual(abspath(self.dummy.file_field.path), abspath(path))

    def tearDown(self):
        self.dummy.file_field.delete()

# skipUnless not available in Django 1.2
# @skipUnless(has_pil, "PIL is required to test ImageField")
class FillingImageFileField(TestCase):

    def setUp(self):
        path = mommy.mock_file_jpeg
        self.fixture_img_file = ImageFile(open(path))

    if has_pil:
        def test_filling_image_file_field(self):
            self.dummy = mommy.make(DummyImageFieldModel)
            field = DummyImageFieldModel._meta.get_field('image_field')
            self.assertIsInstance(field, ImageField)
            import time
            path = "%s/%s/mock-img.jpeg" % (gettempdir(), time.strftime('%Y/%m/%d'))

            from django import VERSION
            if VERSION[1] >= 4:
                # These require the file to exist in earlier versions of Django
                self.assertEqual(abspath(self.dummy.image_field.path), abspath(path))
                self.assertTrue(self.dummy.image_field.width)
                self.assertTrue(self.dummy.image_field.height)

    def tearDown(self):
        self.dummy.image_field.delete()


class FillingCustomFields(TestCase):

    def setUp(self):
        generator_dict = {'test.generic.fields.CustomFieldWithGenerator': gen_value_string}
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)

    def tearDown(self):
        delattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN')

    def test_raises_unsupported_field_for_custom_field(self):
        self.assertRaises(TypeError, mommy.make, CustomFieldWithoutGeneratorModel)

    def test_uses_generator_defined_on_settings_for_custom_field(self):
        obj = mommy.make(CustomFieldWithGeneratorModel)
        self.assertEqual("value", obj.custom_value)

    def test_uses_generator_defined_as_string_on_settings_for_custom_field(self):
        generator_dict = {'test.generic.fields.CustomFieldWithGenerator':
                                'test.generic.generators.gen_value_string'}
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)

        obj = mommy.make(CustomFieldWithGeneratorModel)
        self.assertEqual("value", obj.custom_value)

    def test_uses_generator_defined_on_settings_for_custom_foreignkey(self):
        generator_dict = {'test.generic.fields.CustomForeignKey': 'model_mommy.mommy.make'}
        setattr(settings, 'MOMMY_CUSTOM_FIELDS_GEN', generator_dict)
        obj = mommy.make(CustomForeignKeyWithGeneratorModel, custom_fk__email="a@b.com")
        self.assertEqual('a@b.com', obj.custom_fk.email)


class FillingAutoFields(TestCase):

    def test_filling_AutoField(self):
        obj = mommy.make(DummyEmptyModel)
        field = DummyEmptyModel._meta.get_field('id')
        self.assertIsInstance(field, AutoField)
        self.assertIsInstance(obj.id, int)
