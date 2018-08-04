from django import forms
from django.forms import ModelForm
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, Hidden
from crispy_forms.bootstrap import InlineRadios
from rolepermissions.checkers import has_role
from apps.accounts.roles import Admin
from .constants import Permissions
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from address.forms import AddressField
from apps.core.widgets import QuillInput, ImageInput, DateTimePickerInlineInput
from django.forms import inlineformset_factory

class ClubRegistrationForm(ModelForm):

    logo = forms.ImageField(required=False)
    cover_image = forms.ImageField(required=False)
    slug = forms.CharField(label="Username", help_text="/c/username. This cannot be changed later!")

    class Meta:
        model = Club
        fields = ['name', 'description', 'slug', 'logo', 'cover_image']

    def __init__(self, *args, **kwargs):
        super(ClubRegistrationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.add_input(
            Submit('submit', "Register", css_class="btn-block")
        )

class EventCreationForm(ModelForm):

    venue = AddressField()
    start_date = forms.DateTimeField(
        widget=DateTimePickerInlineInput()
    )
    end_date = forms.DateTimeField(
        widget=DateTimePickerInlineInput()
    )
    od = forms.ChoiceField(
        choices=((True, "Yes"), (False, "No"))
    )
    cover_image = forms.ImageField(
        widget = ImageInput()
    )
    description = forms.CharField(
        widget=QuillInput()
    )
    club = forms.CharField(
        widget=forms.HiddenInput()
    )
    class Meta:
        model = Event
        fields = ['title', 'cover_image', 'start_date', 'end_date', 'venue', 'od', 'description', 'club']
    
    def __init__(self, club, *args, **kwargs):
        super(EventCreationForm, self).__init__(*args, **kwargs)

        self.club_data = club

        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        self.helper.layout = Layout(
            'title',
            'cover_image',
            Div(
                Field('start_date', wrapper_class="col-12 col-md-4"),
                Field('end_date', wrapper_class="col-12 col-md-4"),
                InlineRadios('od'),
                css_class="row"
            ),
            'venue',
            'description',
            Hidden('club', self.club_data),
            Submit('save-event', "Save")
        )

    def clean_club(self):
        if not self.club_data:
            raise ValidationError("Invalid Club")
        return self.club_data

class ClubDetailsForm(ModelForm):

    slug = forms.CharField()
    short_description = forms.CharField(required=False)
    logo = forms.ImageField(required=False, widget=ImageInput())
    cover_image = forms.ImageField(required=False, widget=ImageInput())
    facebook = forms.CharField(required=False)
    twitter = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)

    class Meta:
        model = Club
        fields = ['name', 'short_description', 'description', 'slug', 'logo', 'cover_image', 'facebook', 'twitter', 'phone', 'email']
    
    def __init__(self, user, *args, **kwargs):
        super(ClubDetailsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"

        edit_sensitive_fields = False
        if user.is_superuser or has_role(user, Admin):
            edit_sensitive_fields = True

        SlugField = Field('slug', readonly=True)
        if edit_sensitive_fields:
            SlugField = Field('slug')

        self.helper.layout = Layout(
            'name',
            'short_description',
            'description',
            SlugField,
            Div(
                Field('logo', wrapper_class="col-12 col-md-6"),
                Field('cover_image', wrapper_class="col-12 col-md-6"),
                css_class="row"
            ),
            Div(
                Field('facebook', wrapper_class="col-12 col-md-6"),
                Field('twitter', wrapper_class="col-12 col-md-6"),
                Field('phone', wrapper_class="col-12 col-md-6"),
                Field('email', wrapper_class="col-12 col-md-6"),
                css_class="row"
            )
        )

        self.helper.add_input(
            Submit('save-club', 'Save')
        )

class ClubPermissionsForm(ModelForm):

    permission = forms.ChoiceField(
        choices=Permissions.permissions
    )

    club = forms.CharField(
        widget=forms.HiddenInput()
    )

    class Meta:
        model = ClubMemberPermissions
        fields = ['user', 'club', 'permission']

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Selected user already has the selected permission(s)."
            }
        }
    
    def __init__(self, club, *args, **kwargs):
        super(ClubPermissionsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.club_data = club
        self.helper.layout = Layout(
            Div(
                Field('user', wrapper_class="col-12 col-md-5 my-0"),
                Field('permission', wrapper_class="col-12 col-md-5 my-0"),
                Hidden('club', self.club_data),
                Submit('save-permission', 'Grant', css_class="col-12 col-md-2 h-7"),
                css_class="row align-items-center"
            )
        )

    def clean_club(self):
        print("Cleaning")
        if not self.club_data:
            raise ValidationError("Invalid Club")
        
        return self.club_data

class ODApplicationForm(ModelForm):

    timeSlotStart = forms.DateTimeField(
        widget=DateTimePickerInlineInput(),
        label="Time Slot Start"
    )
    timeSlotEnd = forms.DateTimeField(
        widget=DateTimePickerInlineInput(),
        label="Time Slot End"
    )

    class Meta:
        model = ODSubjects
        fields = ['subject', 'timeSlotStart', 'timeSlotEnd']
    
    def __init__(self, *args, **kwargs):
        super(ODApplicationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

class ODApplicationFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ODApplicationFormHelper, self).__init__(*args, **kwargs)
        self.form_method = "post"
        # self.layout = Layout(
        #     'subject',
        #     ''
        # )
        self.render_required_fields = True

ODApplicationFormset = inlineformset_factory(OD, ODSubjects, form=ODApplicationForm, extra=1)
