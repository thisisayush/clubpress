from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rolepermissions.roles import assign_role, clear_roles

from apps.core.constants import database_keys as dk
from apps.core.models import Departments, DepartmentBranches
# Create your models here.

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and save a user with given email and password.
        """

        if not email:
            raise ValueError('Email is Required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User Model"""
    gender_choices = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other','Other'),
    )

    email = models.EmailField(_('email address'), unique=True, help_text="Your Primary Email Address")
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'),  max_length=30, blank=True)
    date_joined = models.DateField(_('date joined'), auto_now=True)
    is_active = models.BooleanField(_('active'), default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    mobile = models.CharField(max_length=10, blank=True, null=True, help_text="Enter your mobile number, WhatsApp Preferred.")
    gender = models.CharField(_('gender'), choices=gender_choices, max_length=6, null=True, blank=True, help_text="Select your gender, wisely.")
    date_of_birth = models.DateField(_('date of birth'), help_text="Your Date of Birth")
    email_confirmed = models.BooleanField(_('email confirmed'), default=False)
    enrollment_no = models.CharField(max_length = 13, unique=True, help_text="Your Amity Enrollment Number")
    registration_year = models.CharField(max_length=4, help_text="Year of Joining Amity")
    department = models.ForeignKey(Departments, on_delete=models.SET_NULL, null=True, help_text="Select your department e.g. ASET")
    branch = models.ForeignKey(DepartmentBranches, on_delete = models.SET_NULL, null=True, help_text="Select your Branch e.g. ASET - CSE")
    section = models.CharField(max_length = 2, help_text="Section Number e.g. 5")
    batch = models.CharField(max_length = 1, help_text="Class Batch e.g. X or Y")
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name of user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this user
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def change_user_role(self, user, roles):
        """Changes User Role
        
        Requires: django-rolepermissions
        Params:
            user: User Object
            roles: A list containing new roles of the user

        This methods clears the previous roles of the user and replaces them with the new one.
        """

        clear_roles(user)
        for role in roles:
            assign_role(user, role)
        return user

    
    def filter_user_data(search="", sort_by="", sort_order="", start=-1, end=-1):
        """Filter the User Queryset and returns it

        Params:
            search (""): String to match in columns (first_name, last_name, email, address, gender, mobile)
            sort_by (""): Column to sort the data by. Throws TypeError if not String, ValueError if column name not matches with any field.
            sort_order (""): 'asc' for ascending or 'dsc' for descending. Orders in Ascending order if nothing is provided.
            start (-1): Start index for sorted data. Throws TypeError if not int or less than -1.
            end (-1): End Index for sorted data. Throws TypeError if not int or less than -1.
        """
        
        if sort_by == None:
            sort_by = ""

        if type(sort_by) != str:
            raise TypeError("sort_by must be a string, provided " + str(type(sort_by)))
    
        if sort_by != "":
            if sort_by not in [field.name for field in User._meta.get_fields()] :
                raise ValueError("Invalid Column Name %s provided for sort_by " % str(sort_by) )

        if search == None:
            search = ""

        if type(start) != int and start < -1:
            raise TypeError("start index must be a int, provided " + str(type(start)))
        
        if type(end) != int and end < -1:
            raise TypeError("end index must be a int, provided " + str(type(end)))

        query_filter =  Q(first_name__icontains = search) | \
                        Q(last_name__icontains = search) | \
                        Q(email__icontains = search) | \
                        Q(mobile__icontains=search) | \
                        Q(gender__icontains=search) | \
                        Q(enrollment_no__icontains=search) | \
                        Q(department__name__icontains=search) | \
                        Q(branch__name__icontains=search)
        users = None
        
        if start == -1 and end != -1:
            users = User.objects.filter(query_filter)[:end]
        elif start != -1 and end == -1:
            users = User.objects.filter(query_filter)[start:]
        elif start != -1 and end != -1:
            users = User.objects.filter(query_filter)[start:end]
        else:
            users = User.objects.filter(query_filter)

        if sort_by != "":
            if sort_order == "" or sort_order == "asc":
                users = users.order_by(sort_by)
            else:
                users = users.order_by("-"+sort_by)
        
        return users
