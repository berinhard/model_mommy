from django import VERSION
from django.forms import ModelForm


if VERSION < (1, 4):
    from test.generic.models import DummyIPAddressFieldModel

    class DummyIPAddressFieldForm(ModelForm):
        class Meta:
            model = DummyIPAddressFieldModel
else:
    from test.generic.models import DummyGenericIPAddressFieldModel

    class DummyGenericIPAddressFieldForm(ModelForm):
        class Meta:
            model = DummyGenericIPAddressFieldModel