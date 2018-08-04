from .models import Options, DepartmentBranches, Departments
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import get_template
from psycopg2 import IntegrityError

def addOption(key, value, label):
    try:
        option = Options.objects.create(key = key, value = value, label = label)
        return option
    except Exception:
        return False

def getOptions():
    try:
        options = {
            "site_title": getOption("site_title"),
            "support_email": getOption("support_email"),
            "site_description": getOption("site_description"),
            "smtp_server": getOption("smtp_server"),
            "smtp_user": getOption("smtp_user"),
            "smtp_pass": getOption("smtp_pass"),
            "smtp_port": getOption("smtp_port"),
            "send_mails_as": getOption("send_mails_as"),
            "site_url": getOption("site_url")
        }
        return options
    except Exception as e:
        print(e)
        return None

def getOption(key):
    try:
        option = Options.objects.get(key = key)
        return option.value
    except Options.DoesNotExist:
        return None

def setOption(key, value):
    try:
        option = Options.objects.get(key = key)
        option.value = value
        option.save()
        return True
    except Options.DoesNotExist:
        return False

def send_mail(subject, to, template, context):

    try:

        plaintext = get_template("%s/template.txt" % template).render(context)
        html = get_template("%s/template.html" % template).render(context)

        con = mail.get_connection(
            host = getOption("smtp_server"),
            port = getOption("smtp_port"),
            username = getOption("smtp_user"),
            password = getOption("smtp_pass"),
            use_tls = True
        )
        msg = mail.EmailMultiAlternatives(
            subject=subject,
            body = plaintext,
            from_email = getOption("send_mails_as"),
            to = [to],
            connection = con
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as e:
        return False

def addDepartment(name, short_name):
    dept = getDepartment(name)
    if not dept:
        try:
            dept = Departments.objects.create(name=name, short_name=short_name)
            return dept
        except IntegrityError as e:
            print(e)
            return False
    else:
        return dept 

def getDepartment(name):
    try:
        dept = Departments.objects.get(name = name)
        return dept
    except Departments.DoesNotExist:
        return False

def addBranch(name, short_name, dept):
    branch = getBranch(name)

    if not branch:
        try:
            branch = DepartmentBranches.objects.create(name=name, short_name=short_name, department=dept)
            return branch
        except IntegrityError as e:
            print(e)
            return False
    else:
        return branch

def getBranch(name):
    try:
        branch = DepartmentBranches.objects.get(name=name)
        return branch
    except DepartmentBranches.DoesNotExist:
        return False
