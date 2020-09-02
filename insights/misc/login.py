import requests
import uuid

from urllib.parse import urlencode

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from misc.models import Token
from django.shortcuts import get_object_or_404, redirect, render

from insights.settings import CLIENT_ID, CLIENT_SECRET, HOST

def oauth(request):
    res = requests.post(
        "https://github.com/login/oauth/access_token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": request.GET.get("code"),
            "redirect_uri": HOST + "/oauth/redirect",
        },
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    res.raise_for_status()
    data = res.json()

    if not "access_token" in data:
        print("Something went wrong here")
        return redirect("/")

    access_token = data["access_token"]

    res = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": "token %s" % access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    res.raise_for_status()
    data = res.json()

    username = "github:" + data["login"]
    existing = User.objects.filter(username=username)
    if existing:
        user = existing[0]
    else:
        user = User.objects.create_user("github:" + data["login"])

    token = Token.objects.get_or_create(user=user)[0]
    print("Access token updated.")
    token.access = access_token
    token.save()

    login(request, user)
    return redirect("/")


@login_required
def logout_view(request):
    logout(request)
    return redirect("/")


def get_login_url():
    base = "https://github.com/login/oauth/authorize?"
    data = {
        "client_id": CLIENT_ID,
        "UUID": uuid.uuid4(),
        "scope": "user",
        "redirect_uri": HOST + "/oauth/redirect",
    }
    return base + urlencode(data)