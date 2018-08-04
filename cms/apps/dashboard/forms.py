from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import AdminPasswordChangeForm
from rolepermissions.checkers import has_permission
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.core.constants import permissions as p
from apps.accounts.roles import Subscriber, Admin
from apps.core.models import Departments, DepartmentBranches
import datetime
class UserForm(forms.ModelForm):

    gender = forms.ChoiceField(
        choices=User.gender_choices,
        widget = forms.RadioSelect
    )

    mobile = forms.CharField(
        label = "Mobile Number"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'avatar', 'mobile', 'date_of_birth', 'enrollment_no', 'registration_year', 'department', 'branch', 'section', 'batch']

    def __init__(self, user, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "container"
        self.helper.label_class = "font-weight-bold"
        # edit_sensitive_fields = True if has_permission(user, p.EDIT_USERS) else False
        edit_sensitive_fields = False
        emailField = Field('email', wrapper_class="col-12 col-md-6")

        if not edit_sensitive_fields:
            emailField = Field('email', readonly=edit_sensitive_fields, wrapper_class="col-12 col-md-6")
            
        self.helper.layout = Layout(
            Div(
                Field('first_name', wrapper_class='col-12 col-md-6'),
                Field('last_name', wrapper_class='col-12 col-md-6'),
                css_class="row"
            ),
            Div(
                emailField,
                Field('mobile', wrapper_class="col-12 col-md-6"),
                css_class="row"
            ),
            Div(
                InlineRadios('gender', wrapper_class="col-12 col-md-6"),
                Field('date_of_birth', wrapper_class="col-12 col-md-6"),
                css_class="row"
            ),
            'avatar',
            Div(
                Field('enrollment_no', wrapper_class="col-12 col-md-6"),
                Field('registration_year', wrapper_class="col-12 col-md-6"),
                css_class="row"
            ),
            Div(
                Field('department', wrapper_class="col-12 col-md-3"),
                Field('branch', wrapper_class="col-12 col-md-3"),
                Field('section', wrapper_class="col-6 col-md-3"),
                Field('batch', wrapper_class="col-6 col-md-3", read_only=edit_sensitive_fields),
                css_class="row"
            ),
        )
        self.helper.add_input(Submit('user-submit', 'Save'))

    def clean_branch(self):
        valid_branches = DepartmentBranches.objects.filter(department = self.cleaned_data['department'])

        if self.cleaned_data['branch'] not in valid_branches:
            raise ValidationError("Invalid Branch for selected department")
        return self.cleaned_data['branch']

    def clean_registration_year(self):
        try:
            year = int(self.cleaned_data['registration_year'])
        except ValueError:
            raise ValidationError("Please enter a valid year!")
        
        if year < 2005 or year > datetime.datetime.now().year:
            raise ValidationError("Value must be greater than 2002 and less than current year!")
        
        return self.cleaned_data['registration_year']

    def clean_section(self):
        try:
            section = int(self.cleaned_data['section'])
        except ValueError:
            raise ValidationError("Please enter a valid section!")
        
        if section < 1 or section > 99:
            raise ValidationError("Please enter a valid section!")

        return self.cleaned_data['section']
    
    def clean_batch(self):
        if len(self.cleaned_data['batch']) > 1:
            raise ValidationError('Enter a valid batch!')
        
        return self.cleaned_data['batch']
    
    def clean_mobile(self):
        if len(self.cleaned_data['mobile']) > 10:
            raise ValidationError('Enter a valid mobile number!')
        for digit in self.cleaned_data['mobile']:
            try:
                int(digit)
            except ValueError as e:
                raise ValidationError("Enter a valid mobile number")
        
        return self.cleaned_data['mobile']

class PasswordChangeForm(AdminPasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.pop("autofocus", None)

        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        
        self.helper.add_input(Submit('password-change', 'Change Password'))

class RolesForm(forms.Form):

    roles = forms.MultipleChoiceField(
        choices = (
            (Subscriber.display_name, Subscriber.title),
            (Admin.display_name, Admin.title)
        )
    )

    def __init__(self, *args, **kwargs):
        super(RolesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"

        self.helper.add_input(Submit('change-role', 'Save Role(s)'))

class OptionsForm(forms.Form):

    site_title = forms.CharField(label = "Site Title", required=False)
    site_description = forms.CharField(label = "Site Description",required = False)
    support_email = forms.EmailField(label = "Support Email", required=False)
    site_url = forms.URLField(label = "Site URL", required=True)
    smtp_server = forms.CharField(label = "SMTP Server")
    smtp_user = forms.CharField(label = "SMPT User")
    smtp_pass = forms.CharField(label = "SMTP Password")
    smtp_port = forms.CharField(label = "SMTP Port")
    send_mails_as = forms.EmailField(label = "Send Email As")

    def __init__(self, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        
        self.helper.layout = Layout(
            Div(
                'site_title',
                'site_url',
                'site_description',
                'support_email',
                css_class="card my-3 my-md-5 p-3"
            ),
            Div(
                'smtp_server',
                'smtp_user',
                'smtp_pass',
                'smtp_port',
                'send_mails_as',
                css_class="card my-3 my-md-5 p-3"
            )
        )

        self.helper.add_input(Submit('save-options', 'Save Options'))