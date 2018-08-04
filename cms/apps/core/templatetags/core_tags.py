from django.template.defaultfilters import register

@register.filter
def modulo(num, val):
    return num % val

@register.filter
def subtract(value, arg):
    return value - arg