from django import VERSION
from django.forms import ModelForm


if VERSION < (1, 4):
    from test.generic.models import DummyIPAddressFieldModel

    class DummyIPAddressFieldForm(ModelForm):
        class Meta:
            fields = ('ipv4_field',)
            model = DummyIPAddressFieldModel
else:
    from test.generic.models import DummyGenericIPAddressFieldModel

    class DummyGenericIPAddressFieldForm(ModelForm):
        class Meta:
            fields = ('ipv4_field', 'ipv6_field', 'ipv46_field')
            model = DummyGenericIPAddressFieldModel
