# Overwriting the default file input on the form

from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    # Setting custom values for the text on the input
    clear_checkbox_label = _('Remove')
    initial_text = ('Current Image')
    input_text = ('')
    template_name = 'custom_widget_templates/custom_clearable_file_input.html'
