from django import forms
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

class QuillInput(forms.TextInput):
    
    def render(self, name, value, attrs=None):
        super().render(name, value, attrs)
        flat_attrs = flatatt(attrs)

        html = '''
            <div class="bg-white">
                <div id="%(id)s" class="">
                    %(value)s
                </div>
                <textarea id="%(id)s_html" name="%(name)s" style="height:0;width:0;visiblity: none;opacity:0;">
                    %(value)s
                </textarea>
            </div>
            <script>
                require(['jquery', 'quill'], function($, Quill){
                    var toolbarOptions = [
                        ['bold', 'italic', 'underline', 'italic'],
                        [{'list':'ordered'}, {'list':'bullet'}],
                        ['clean']
                    ];
                    var quill = new Quill("#%(id)s", {
                        modules: {
                            toolbar: toolbarOptions
                        },
                        theme: 'snow'
                    });
                    $("#%(id)s .ql-editor").on("keydown blur input", function(e){
                        $("#%(id)s_html").html($(this).html());
                    });
                });
            </script>
        ''' % {'id': attrs['id'], 'value': value, 'name': name}

        return mark_safe(html)

    class Media:
        css = {"all": ('https://cdn.quilljs.com/1.0.0/quill.snow.css',) }

class ImageInput(forms.ClearableFileInput):

    template_name = 'core/forms/widgets/input-image.html'
    initial_text = _('Current')
    input_text = _('Select New')
    clear_checkbox_label = _('Remove?')

class DateTimePickerInlineInput(forms.TextInput):

    template_name = 'core/forms/widgets/datetimepickerinline.html'

    class Media:
        css = {"all": ("assets/css/bootstrap-datetimepicker.min.css",)}

class DatePickerInput(forms.TextInput):

    template_name = 'core/forms/widgets/datepicker.html'

    class Media:
        css = {"all": ("assets/css/bootstrap-datetimepicker.min.css",)}