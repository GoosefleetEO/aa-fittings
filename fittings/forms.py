from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import Category


# Create your forms here.
class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
