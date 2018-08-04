from django import forms
from crispy_forms.helper import FormHelper

class CrispyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CrispyForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"

class DynamicForm():

    class FieldHandler():
        formfields = {}

        def __init__(self, fields):
            for field in fields:
                options = self.get_field_options(field)
                f = getattr(self, 'create_field_for_'+field['type'])(field, options)
                self.formfields[field['name']] = f
        
        def get_field_options(self, field):
            options = {}
            options['label'] = field['label']
            options['help_text'] = field.get("help_text", None)
            options['required'] = bool(field.get("required", 0) )
            return options
        
        def create_field_for_text(self, field, options):
            options['max_length'] = int(field.get("max_length", "225") )
            return forms.CharField(**options)

        def create_field_for_textarea(self, field, options):
            options['max_length'] = int(field.get("max_value", "9999999") )
            return forms.CharField(widget=forms.Textarea, **options)

        def create_field_for_integer(self, field, options):
            options['max_value'] = int(field.get("max_value", "999999999") )
            options['min_value'] = int(field.get("min_value", "-999999999") )
            return forms.IntegerField(**options)

        def create_field_for_radio(self, field, options):
            options['choices'] = [ (c['value'], c['name'] ) for c in field['choices'] ]
            return forms.ChoiceField(widget=forms.RadioSelect,   **options)

        def create_field_for_select(self, field, options):
            options['choices']  = [ (c['value'], c['name'] ) for c in field['choices'] ]
            return forms.ChoiceField(  **options)

        def create_field_for_checkbox(self, field, options):
            return forms.BooleanField(widget=forms.CheckboxInput, **options)
    
    def __init__(self, fields):
        fh = self.FieldHandler(fields)

        return type('DynaForm', (CrispyForm), fh.formfields)