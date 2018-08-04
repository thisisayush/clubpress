from django.shortcuts import render, redirect, reverse
from .forms import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .utils import *
from django.http import Http404
from rolepermissions.checkers import has_permission
from .constants import Permissions as p
# Create your views here.

def ClubIndexView(request, slug):
    club = getClubBySlug(slug)
    if club is not None:

        club_meta = {
            "members": getClubMembers(club),
            "team": getClubMembers(club, True)
        }

        return render(request, "club/index.html", {"club": club, "club_meta": club_meta})
    else:
        raise Http404("The page you're looking was not found!")

def EventView(request, slug, id):

    club = getClubBySlug(slug)
    
    try:
        event = Event.objects.get(pk = id)
    except Event.DoesNotExist:
        raise Http404("Event Not Found!")

    is_registered = IsUserRegisteredForEvent(event, request.user)
    event_meta = getEventMeta(event)
    rsvp = getRSVPForEvent(event, request.user)

    return render(request, "club/event.html", {"club": club, "event": event, "event_meta": event_meta, 'is_registered': is_registered, 'rsvp': rsvp})

@login_required
def SetRSVPView(request, slug, id, rsvp):
    club = getClubBySlug(slug)
    event = getEventById(id)

    if club is None or event is None:
        raise Http404("Club/Event doesn't exist.")
    
    if IsUserRegisteredForEvent(event, request.user):
        if rsvp not in [r[0] for r in EventRegistration.rsvp_choices]:
            return render(request, "error.html", {"error": "Invalid Choice for RSVP"})
        
        if setRSVPForEvent(event, request.user, rsvp):
            return redirect(reverse("club:event", kwargs={"slug": slug, "id": id}))
    else:
        return redirect(reverse("club:register-event", kwargs={"slug": slug, "id": id}))

@login_required
def EventEditView(request, slug, id):
    club = getClubBySlug(slug)
    event = None
    if club is None:
        raise Http404("Club Doesn't exist")
    
    if not request.user.is_superuser and not hasClubPermission(club, request.user, p.EDIT_EVENT):
        raise PermissionDenied("You do not have permissions to edit/create event for %s" % (club.name))
    
    eventForm = EventCreationForm(club=club, instance=event)

    if id != -1:
        try:
            event = Event.objects.get(pk=id)
            eventForm = EventCreationForm(club=club, instance=event)
        except Event.DoesNotExist:
            raise Http404("Event Doesn't Exist")
    
    if request.method == "POST":
        print(request.POST)
        eventForm = EventCreationForm(club=club, data=request.POST or None, files=request.FILES or None, instance=event)
        if eventForm.is_valid():
            event = eventForm.save()
            if id == -1:
                return redirect(reverse("club:edit-event", kwargs={"slug": slug, "id": event.id}))
            eventForm = EventCreationForm(club=club, instance=event)
    print(eventForm.errors)
    return render(request, "club/event-edit.html", {"form": eventForm})

@login_required
def RegisterEventView(request, slug, id):
    
    club = getClubBySlug(slug)
    event = getEventById(id)
    if club is None or event is None:
        raise Http404("Club/Event Doesn't Exist")
    
    if IsUserRegisteredForEvent(event, request.user):
        return redirect(reverse("club:event", kwargs={"slug":club.slug, "id":event.id})+"?registered=True")
    
    if request.GET.get('register', False) == "true":
        if RegisterUserForEvent(event, request.user):
            return redirect(reverse("club:event", kwargs={"slug":club.slug, "id":event.id})+"?registered=True")
        else:
            return render("error.html", {"error": "Unable to Register for the event! Try again?"})
    
    return render(request, "club/event-register.html", {"club": club, 'event': event})

@login_required
def ClubRegistrationView(request):
    
    form = None
    if request.method == "POST":
        form = ClubRegistrationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            club = form.save()
            if initializeClubRoles(club, request.user):
                return render(request, "success.html", {"message": "Club Registered Successfully!"})
            else:
                return render(request, "error.html", {"error": "Unable to initialize Roles!"})
    else:
        form = ClubRegistrationForm()

    return render(request, "club/club-register.html", {"form": form})

@login_required
def ClubEditView(request, slug):
    club = getClubBySlug(slug)

    if club is not None:
        if request.user.is_superuser or hasClubPermission(club, request.user, p.EDIT_PROFILE):
            form = ClubDetailsForm(user=request.user, instance=club)
            permissionForm = ClubPermissionsForm(club=club)
            
            if request.method == "POST":
                if 'save-club' in request.POST:
                    form = ClubDetailsForm(user=request.user, data=request.POST or None, files=request.FILES or None, instance=club)
                    if form.is_valid():
                        form.save()
                        club = getClubBySlug(slug)
                        form = ClubDetailsForm(user=request.user, instance=club)
                if 'save-permission' in request.POST:
                    permissionForm = ClubPermissionsForm(club=club, data=request.POST or None)

                    if permissionForm.is_valid():
                        permissionForm.save()

                        permissionForm = ClubPermissionsForm(club=club)
                    
                    print(permissionForm.errors)
            permissions = getClubPermissions(club)
            return render(request, "club/club-edit.html", {'form': form, 'club': club, 'permissionForm': permissionForm, 'permissions': permissions})
        else:
            raise PermissionDenied("You do not have permissions to perform the requested operation!")
    else:
        raise Http404("The Page you requested was not found!")

@login_required
def ClubJoinView(request, slug):
    
    club = getClubBySlug(slug)

    if club is None:
        raise Http404("Club Doesn't Exist")
    
    club_meta = {
        "members": getClubMembers(club),
        "team": getClubMembers(club, True)
    }
    if IsClubMember(club, request.user):
        return redirect(reverse("club:club-home", kwargs={"slug":club.slug})+"?registered=True")
    
    if request.GET.get('register', False) == "true":
        if addMemberToClub(club, request.user):
            return redirect(reverse("club:club-home", kwargs={"slug":club.slug})+"?registered=True")
        else:
            return render("error.html", {"error": "Unable to Register for the club! Try again?"})
    
    # extra_questions = getEventQuestions(event)

    return render(request, "club/club-join.html", {"club": club, "club_meta": club_meta})

@login_required
def ApplyODView(request, slug, id):

    club = getClubBySlug(slug)
    event = getEventById(id)
    if club is None or event is None:
        raise Http404("Club/Event Doesn't Exist")
    
    if not IsUserRegisteredForEvent(event, request.user):
        return redirect(reverse("club:register-event", kwargs={"slug":club.slug, "id":event.id}))

    if request.method == "POST":
        pass

    formset = None
    helper = ODApplicationFormHelper()
    helper.add_input(Submit("submit", "Submit"))
    helper.template = 'bootstrap/table_inline_formset.html'
    helper.form_id = "odForm"
    
    try:
        od = OD.objects.get(user=request.user, event=event)
    except OD.DoesNotExist:
        try:
            od = OD.objects.create(user=request.user, event=event)
        except IntegrityError as e:
            render(request, "error.html", {"error": str(e)})

    if request.method == "POST":
        print(od)
        formset = ODApplicationFormset(request.POST or none, instance=od)
        if formset.is_valid():
            if od is not None:
                for form in formset:
                    if form not in formset.deleted_forms:
                        if not form.instance.od:
                            form.instance.od=od
                        if not (form.empty_permitted and not form.has_changed()):
                            form.save()
                    # if not sub.od:
                    #     sub.od = od
                    # sub.save()
                for form in formset.deleted_forms:
                    instance = form.instance
                    if instance.pk:
                        try:
                            instance.delete()
                        except Exception as e:
                            print(e)
                formset = ODApplicationFormset(instance=od)
            else:
                render(request, "error.html", {"error": "Unknown Error Occured!"})
        else:
            print("Formser has erros")
    else:
        if od is None:
            render(request, "error.html", {"error": "Unknown Error Occured!"})
        else:
            formset = ODApplicationFormset(instance=od)
    return render(request, "club/apply-od.html", {'club': club, 'event': event, 'formset': formset, 'helper': helper})