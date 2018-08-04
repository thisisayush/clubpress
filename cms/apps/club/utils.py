from .models import *
from psycopg2 import IntegrityError
from apps.core.forms import DynamicForm
import json

def initializeClubRoles(club, user):

    roles = (
        ("admin", "Admin", False),
        ("member", "Member", False),
        ("creator", "Creator", False)
    )
    
    for role in roles:
        try:
            r = ClubRoles.objects.create(title=role[0], label=role[1], club=club, mutable=role[2])
            ClubMemberRoles.objects.create(user=user, role=r, club=club)
        except IntegrityError:
            pass

        try:
            r = ClubRoles.objects.get(title=role[0], club=club)
            ClubMemberRoles.objects.get(role=r, user=user, club=club)
        except ClubRoles.DoesNotExist:
            return False
        except ClubMemberRoles.DoesNotExist:
            return False
    
    return True

def getClubRole(club, role):
    try:
        return ClubRoles.objects.get(title=role, club=club)
    except ClubRoles.DoesNotExist:
        return False
        
def getClubBySlug(slug):

    try:
        c = Club.objects.get(slug=slug)
        return c
    except Club.DoesNotExist:
        return None

def getMembersList(ClubMemberRolesQueryset):
    obj = {}
    for member in ClubMemberRolesQueryset:
        if member.user in obj:
            obj[member.user]['roles'].append(member.role)
        else:
            obj[member.user] = {"user": member.user, "roles": []}
    return [obj[member] for member in obj]

def ClubMembersSerializer(club, team_only=False):
    try:
        members = ClubMemberRoles.objects.filter(club=club)
        if team_only:
            members = members.exclude(role__title="member")
        return getMembersList(members)    
        
    except Exception as e:
        print(e)
        return None

def getClubMembers(club, team_only=False):
    try:
        members = ClubMembersSerializer(club, team_only)
        
        if members is not None:
            return members
        else:
            return []
    except Exception as e:
        print(e)
        return []

def isClubAdmin(club, user):
    try:
        ClubMemberRoles.objects.get(user=user, club=club, role__title="admin")
        return True
    except ClubMemberRoles.DoesNotExist:
        return False
    except Exception as e:
        return False

def hasClubPermission(club, user, permission):
    
    if isClubAdmin(club, user):
        return True
    
    try:
        ClubMemberPermissions.objects.get(club=club, user=user, permission=permission)
        return True
    except ClubMemberPermissions.DoesNotExist:
        return False
    except Exception as e:
        return False

def getClubPermissions(club):
    try:
        perms = ClubMemberPermissions.objects.filter(club=club)
        return perms
    except Exception as e:
        print(e)
        return []

def getEventById(id):
    try:
        event = Event.objects.get(pk=id)
        return event
    except Event.DoesNotExist:
        return None

def getEventQuestions(event):
    try:
        questions = EventRegistrationQuestions.objects.filter(event=event).order_by('order')
        q = []
        for question in question:
            obj = {}
            obj['label'] = question['question']
            obj['type'] =   question['input_type']
            obj['required'] = question['required']
            meta = json.loads(question['input_meta'])
            obj['min_length'] = meta.get('min_length', -9999999)
            obj['max_length'] = meta.get('max_length', 9999999)
            obj['choices'] = meta.get('choices', [])
            q.append(obj)
        form = DynamicForm.get_form()
        return form
    except Exception as e:
        return []

def getEventMeta(event):

    return []

def RegisterUserForEvent(event, user):
    if IsUserRegisteredForEvent(event, user):
        return True

    try:
        id = EventRegistration.objects.create(event=event, user=user)
        return True
    except IntegrityError as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False

def IsUserRegisteredForEvent(event, user):
    try:
        EventRegistration.objects.get(event=event, user=user)
        return True
    except EventRegistration.DoesNotExist:    
        return False

def getRSVPForEvent(event, user):
    if not IsUserRegisteredForEvent(event, user):
        return False
    return EventRegistration.objects.get(event=event, user=user).rsvp

def setRSVPForEvent(event, user, rsvp):
    if rsvp not in [r[0] for r in EventRegistration.rsvp_choices]:
        return False
    if not IsUserRegisteredForEvent(event, user):
        return False
    try:
        e = EventRegistration.objects.get(event=event, user=user)        
        e.rsvp = rsvp
        e.save()
        return True
    except Exception as e:
        return False

def addMemberToClub(club, user, role='member'):
    try:
        is_member = True if role=="member" else False
        role = getClubRole(club, role)
        if not role:
            return False
        return ClubMemberRoles.objects.create(user=user, club=club, role=role, pending=is_member)
    except IntegrityError as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False

def IsClubMember(club, user):
    try:
        if len(ClubMemberRoles.objects.filter(club=club, user=user)) > 0:
            return True
        else:
            return False
    except Exception as e:
        return False