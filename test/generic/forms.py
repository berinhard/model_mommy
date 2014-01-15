from django.forms import ModelForm

from test.generic.models import DummyIPAddressesFieldModel


class DummyIPAddressesFieldForm(ModelForm):
    class Meta:
        model = DummyIPAddressesFieldModel