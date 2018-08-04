from django.db import models
from apps.accounts.models import User
from address.models import AddressField

# Create your models here.

class TimeStampModel(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Club(TimeStampModel):

    name = models.CharField(max_length = 500)
    short_description = models.CharField(max_length = 500, null=True, default="Short description. Change in profile.")
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(null=True)
    cover_image = models.ImageField(null=True)

    facebook = models.URLField(null=True)
    twitter = models.URLField(null=True)
    phone = models.CharField(max_length=10, null=True)
    email = models.EmailField(null=True)


    def __str__(self):
        return self.name

class ClubRoles(TimeStampModel):

    title = models.CharField(max_length = 50)
    label = models.CharField(max_length = 50)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    mutable = models.BooleanField(default=True)

    class Meta:
        unique_together = (('title', 'club'))
    
    def __str__(self):
        return "%s -> %s" % (self.club.name, self.label)

class ClubMemberRoles(TimeStampModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(ClubRoles, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete = models.CASCADE)
    pending = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, related_name="approved_by", null=True, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('user', 'role'))
    
    def __str__(self):
        return "%s -> %s" % (self.club.name, self.role.label)

class ClubMemberPermissions(TimeStampModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    permission = models.CharField(max_length=50)

    class Meta: 
        unique_together = (('user', 'club', 'permission'))
    
    def __str__(self):
        return "%s -> %s" % (self.club.name, self.permission)

class Event(TimeStampModel):

    title = models.CharField(max_length = 255)
    cover_image = models.ImageField(null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = AddressField(on_delete = models.DO_NOTHING)
    od = models.BooleanField(default=False)
    description = models.TextField(null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):

    rsvp_choices = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('maybe', 'Maybe')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rsvp = models.CharField(choices=rsvp_choices, max_length = 5, default="yes")

    def __str__(self):
        return self.user.name
    
    class Meta:
        unique_together = (('user','event'))

class EventRegistrationQuestions(models.Model):

    input_choices = (
        ('text', 'TextBox'),
        ('textarea', 'TextArea'),
        ('radio', 'Single Choice Radio'),
        ('select', 'Select'),
        ('number', 'Number')
    )

    question = models.CharField(max_length = 1000)
    input_type = models.CharField(choices=input_choices, max_length=40)
    input_meta = models.TextField(null=True)
    required = models.BooleanField(default = False)
    order = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('event','order'))
    
    def __str__(self):
        return self.question

class EventRegistrationAnswers(models.Model):
    question = models.ForeignKey(EventRegistrationQuestions, on_delete=models.CASCADE)
    answer = models.TextField(null=True)
    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('question', 'registration'))
    
    def __str__(self):
        return self.answer

class ODSlot(models.Model):

    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()


class OD(TimeStampModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="od_event")
    role = models.CharField(max_length=255, default="participant")    
    class Meta:
        unique_together = (('user', 'event'))

    def __str__(self):
        return "%s - %s" % (self.user.get_full_name(), self.role)

class ODSubjects(models.Model):

    status_choices = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    od = models.ForeignKey(OD, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    timeSlotStart = models.DateTimeField()
    timeSlotEnd = models.DateTimeField()
    status = models.CharField(choices=status_choices, max_length=10, default="pending")
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approved_by_user", null=True)

    class Meta:
        unique_together = (('od', 'subject', 'timeSlotStart'))
    
    def __str__(self):
        return self.subject
