from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import UniCategory


# Create your forms here.
class CategoryForm(ModelForm):
    class Meta:
        model = UniCategory
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
