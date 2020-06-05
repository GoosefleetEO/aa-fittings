from django.forms import ModelForm
from django.forms.widgets import TextInput, NumberInput
from .models import UniCategory
from django.contrib.admin.widgets import FilteredSelectMultiple


# Create your forms here.
class CategoryForm(ModelForm):
    class Meta:
        model = UniCategory
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
