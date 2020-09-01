from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from insights.settings import APP_ID, CLIENT_ID, CLIENT_SECRET, HOST
from misc.models import Repo, Token, Artifact, Run
from github import GithubIntegration
from github import Github
from urllib.parse import urlencode
import uuid
import jwt
import time
import requests
from django.contrib.auth.decorators import login_required


def index(request):
    base = "https://github.com/login/oauth/authorize?"
    data = {
        "client_id": CLIENT_ID,
        "UUID": uuid.uuid4(),
        "scope": "user",
        "redirect_uri": HOST + "/oauth/redirect",
    }
    context = {"loginURL": base + urlencode(data)}
    if request.user.is_authenticated:
        context["repos"] = Repo.objects.filter(user=request.user)

    return render(request, "misc/index.html", context)


@login_required
def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def add_repo(request):
    if request.POST:
        repo = Repo.objects.get_or_create(nwo=request.POST["repo"], user=request.user)
        return redirect("/")

    repos = []
    access = Token.objects.get(user=request.user).access
    res = requests.get(
        "https://api.github.com/user/installations",
        headers={
            "Authorization": "token %s" % access,
            "Accept": "application/vnd.github.machine-man-preview+json",
        },
    )
    res.raise_for_status()

    data = res.json()
    for installation in data["installations"]:
        res = requests.get(
            "https://api.github.com/user/installations/%s/repositories"
            % installation["id"],
            headers={
                "Authorization": "token %s" % access,
                "Accept": "application/vnd.github.machine-man-preview+json",
            },
        )
        res.raise_for_status()
        repo_data = res.json()
        for repository in repo_data["repositories"]:
            repos.append(repository["full_name"])

    context = {"repos": repos}
    return render(request, "misc/add-repo.html", context)


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
def show_repo(request, pk):
    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    context = {"repo": repo}
    return render(request, "misc/show-repo.html", context)


@login_required
def artifacts(request, pk):
    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    filtering = request.GET.get('filter')
    sorting = request.GET.get('sort')
    kwargs = {
        "run__workflow__repo": repo
    }
    if filtering == 'expired-only':
        kwargs["expired"] = True
    if filtering == 'active-only':
        kwargs["expired"] = False

    order = ["-created_at"]
    if sorting == 'size':
        order = ["-size_in_bytes", "-created_at"]

    context = {
        "repo": repo,
        "artifacts": Artifact.objects.filter(**kwargs).order_by(*order),
    }
    return render(request, "misc/artifacts.html", context)


@login_required
def runs(request, pk):
    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    context = {"repo": repo, "runs": Run.objects.filter(workflow__repo=repo)}
    return render(request, "misc/runs.html", context)
