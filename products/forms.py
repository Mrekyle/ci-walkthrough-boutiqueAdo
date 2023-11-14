from django import forms
from .widgets import CustomClearableFileInput

from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        """
            Defining what model to be used on the form
        """
        model = Product
        # Includes all fields from the product model
        fields = '__all__'

    image = forms.ImageField(
        label='Image', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        # For loop for creating a list of the categories friendly names
        friendly_names = [(c.id, c.get_friendly_name())
                          for c in categories]

        # Setting the fields in a drop down box for the friendly names of the categories. Instead of an id or name
        self.fields['category'].choices = friendly_names

        # Adding the rest of the fields with set classes to the form
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
