from .models import Token
from django.shortcuts import render

def request_headers(user):
    return {
        "Authorization": "token %s" % get_access_token_for_user(user),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def get_access_token_for_user(user):
    return Token.objects.get(user=user).access


def handler404(request, *args, **argv):
    response = render(request, 'misc/404.html', {})
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render(request, 'misc/500.html', {})
    response.status_code = 500
    return response