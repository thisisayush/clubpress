from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from rolepermissions.checkers import has_permission
from rolepermissions.roles import assign_role

from apps.core.constants import permissions as p

from .forms import LoginForm, UserSignupForm, EmailCollectionForm
from .models import User
from .roles import Subscriber
from .utils import *
from apps.dashboard.forms import PasswordChangeForm

def isUserLoggedIn(request):
    if request.user.is_authenticated:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def LoginView(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    form = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                if user.email_confirmed == True or user.is_superuser:
                    login(request, user)
                    return redirect(request.GET.get('next') if request.GET.get('next', False) else settings.LOGIN_REDIRECT_URL)
                else:
                    form.add_error(None, "Your account isn't activated. Please Check your email for activation mail or send a new one.")
            else:
                try:
                    user = User.objects.get(email=form.cleaned_data['email'])
                    if not user.is_active:
                        form.add_error(
                            None, "Your Login has been suspended. Contact Support for further info.")
                    else:
                        form.add_error(
                            None, "Username and Password doesn't match. Re-check the details. Password is case-sensitive.")
                except ObjectDoesNotExist as e:
                    form.add_error(
                        None, "No account exists with the given email.")
    else:
        form = LoginForm()
    
    loggedout = False
    if request.GET.get("loggedout"):
        loggedout = True
    return render(request, 'accounts/login.html', {'form': form, "logged_out": loggedout})


def LogoutView(request):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    logout(request)
    return redirect("%s?loggedout=true"%settings.LOGIN_URL)


def UserSignupView(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            assign_role(user, Subscriber)
            user = authenticate(
                email=request.POST['email'], password=request.POST['password1'])

            if user is not None:
                if SendAccountActivationEmail(user.email):
                    return render(request, "success.html", {"message": "Account created successfully! Please check your email for activation email to activate your account."})
                else:
                    return render(request, "error.html", {"message": "Unable to send Account Activation Email. Contact Support."})
    else:
        form = UserSignupForm()
    if request.GET.get("via"):
        via = request.GET.get("via")
    else:
        via = False
    return render(request, 'accounts/register.html', {'form': form, 'via': via})


def PasswordResetView(request):
    logout(request)
    form = None
    if request.method == "POST":
        form = EmailCollectionForm(request.POST)
        if form.is_valid():
            res = sendPasswordResetEmail(form.cleaned_data['email'])
            if res:
                return render(request, "accounts/mail-sent.html")
    else:
        form = EmailCollectionForm()

    return render(request, "accounts/forgot-password.html", {"form": form})

def ResendAccountActivationView(request):
    logout(request)
    form = None
    if request.method == "POST":
        form = EmailCollectionForm(request.POST)
        if form.is_valid():
            res = SendAccountActivationEmail(form.cleaned_data['email'])
            if res:
                return render(request, "accounts/mail-sent.html", {"action": "Activate your Account"})
    else:
        form = EmailCollectionForm()

    return render(request, "accounts/account-activation.html", {"form": form})

def PasswordResetTokenValidateView(request, uidb64=None, token=None):

    if uidb64 is None or token is None:
        raise Http404("Page not found!")
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        return render(request, "error.html", {"error": e})
    
    form = PasswordChangeForm(user)
    
    if request.method == "POST":
    
        if PasswordResetTokenGenerator().check_token(user, token):
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                return render(request, "success.html", {"message": "Password Updated Successfuly!"})
        else:
            return render(request, "error.html", {"error": "The Reset Link is no longer valid. Generate a new one."})
    
    return render(request, "accounts/forgot-password-change.html", {"token": token, 'form': form})

def ActivateAccountTokenValidateView(request, uidb64=None, token=None):

    if uidb64 is None or token is None:
        raise Http404("Page not found!")
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        return render(request, "error.html", {"error": e})
    
    if AccountActivationTokenGenerator().check_token(user, token):
        if ActivateUserAccount(user):
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return render(request, "error.html", {"error": "Unknown Error Occured while activating your account."})
    else:
        return render(request, "error.html", {"error": "The Activation Link is no longer valid. Generate a new one."})

    return render(request, "accounts/forgot-password-change.html", {"token": token, 'form': form})

@login_required
def SuspendUser(request, userid):

    if has_permission(request.user, p.SUSPEND_USERS):
        try:
            user = User.objects.get(pk=userid)
            if user == request.user:
                raise PermissionDenied("Cannot Set Current User as Inactive")
            user.is_active = False
            user.save()
            return redirect(request.GET.get('next') if request.GET.get('next', False) else reverse('dashboard:edit-user', args=[user.id]))
        except ObjectDoesNotExist as e:
            raise Http404("User doesn't exist.")
    else:
        raise PermissionDenied(
            "You do not have permissions to suspend/enable users.")


@login_required
def EnableUser(request, userid):

    if has_permission(request.user, p.SUSPEND_USERS):
        try:
            user = User.objects.get(pk=userid)
            user.is_active = True
            user.save()
            return redirect(request.GET.get('next') if request.GET.get('next', False) else reverse('dashboard:edit-user', args=[user.id]))
        except ObjectDoesNotExist as e:
            raise Http404("User doesn't exist")
    else:
        raise PermissionDenied(
            "You do not have permissions to suspend/enable users.")

@login_required
def ActivateUser(request, userid):

    if has_permission(request.user, p.SUSPEND_USERS):
        try:
            user = User.objects.get(pk=userid)
            user.email_confirmed = True
            user.save()
            return redirect(request.GET.get('next') if request.GET.get('next', False) else reverse('dashboard:edit-user', args=[user.id]))
        except ObjectDoesNotExist as e:
            raise Http404("User doesn't exist")
    else:
        raise PermissionDenied(
            "You do not have permissions to activate users.")


@login_required
def RemoveUser(request, userid):

    if has_permission(request.user, p.DELETE_USERS):
        if request.method == "GET":
            return render(
                request,
                'confirm-action.html',
                {
                    'action': 'Delete User',
                    'value': userid,
                    'key': 'id'
                }
            )
        if 'yes' in request.POST:
            try:
                user = User.objects.get(id=userid)
                if request.user == user:
                    raise PermissionDenied(
                        "Deletion of self accounts is banned!")
                user.delete()
                return redirect(request.GET.get('next') if request.GET.get('next', False) else reverse('dashboard:list-users'))
            except User.DoesNotExist:
                raise Http404("User Doesn't Exist")
        else:
            return redirect(reverse('dashboard:list-users'))
    else:
        raise PermissionDenied("You Do not have permissions to remove users.")

@login_required
def AutocompleteUsersListView(request): 

    if has_permission(request.user, p.READ_USERS):
        users = []
        if request.GET.get('term', False):
            term = request.GET.get('term')
            users = User.filter_user_data(search=term)
        else:
            users = User.objects.all()
        data = []
        for user in users:
            obj = {}
            obj['id'] = user.id
            obj['value'] = user.email
            obj['label'] = "%s ( %s ) [ %s ]" % (user.get_full_name(), user.email, str(user.id))
            data.append(obj)
        return JsonResponse(data, safe=False)
    else:
        raise PermissionDenied("You Do not have permissions to list users!")