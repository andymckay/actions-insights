from .models import Token

def request_headers(user):
    return {
        "Authorization": "token %s" % get_access_token_for_user(user),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def get_access_token_for_user(user):
    return Token.objects.get(user=user).access