from django.forms import ModelForm


from test.generic.models import DummyGenericIPAddressFieldModel


class DummyGenericIPAddressFieldForm(ModelForm):
    class Meta:
        fields = ('ipv4_field', 'ipv6_field', 'ipv46_field')
        model = DummyGenericIPAddressFieldModel
