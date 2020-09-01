from .models import Token

def get_access_token_for_user(user):
    return Token.objects.get(user=user).access