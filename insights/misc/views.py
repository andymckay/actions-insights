from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from insights.settings import CLIENT_ID, CLIENT_SECRET, HOST

from urllib.parse import urlencode
import uuid

import requests


def index(request):
    base = "https://github.com/login/oauth/authorize?"
    data = {
        "client_id": CLIENT_ID,
        "UUID": uuid.uuid4(),
        "scope": "user",
        "redirect_uri": HOST + "/oauth/redirect",
    }
    context = {"loginURL": base + urlencode(data)}
    return render(request, "misc/index.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")


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
    login(request, user)
    return redirect("/")
