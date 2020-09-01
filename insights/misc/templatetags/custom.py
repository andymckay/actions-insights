import datetime

from django import template

register = template.Library()


@register.filter(name="expiration")
def expiration(value):
    return value + datetime.timedelta(days=90)
