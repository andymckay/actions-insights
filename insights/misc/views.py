import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from misc.importer import import_repo
from misc.login import get_login_url
from misc.models import Artifact, Repo, Run, Token, Workflow
from misc.utils import request_headers


def index(request):
    context = {"loginURL": get_login_url(), "repos": None, "counts": {}}
    if request.user.is_authenticated:
        context["repos"] = Repo.objects.filter(user=request.user)
        for repo in context["repos"]:
            repo.workflow_count = Workflow.objects.filter(repo=repo).count()
            repo.run_count = Run.objects.filter(workflow__repo=repo).count()
            repo.artifact_count = Artifact.objects.filter(
                run__workflow__repo=repo
            ).count()

    return render(request, "misc/index.html", context)


@login_required
def add_repo(request):
    if request.POST:
        repo = Repo.objects.get_or_create(nwo=request.POST["repo"], user=request.user)[
            0
        ]
        return import_repo(request, repo.pk)

    repos = []
    res = requests.get(
        "https://api.github.com/user/installations",
        headers={
            "Authorization": "token %s" % get_access_token_for_user,
            "Accept": "application/vnd.github.machine-man-preview+json",
        },
    )
    res.raise_for_status()

    added = []
    toAdd = []
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
            if Repo.objects.filter(
                user=request.user, nwo=repository["full_name"]
            ).exists():
                added.append(repository)
            else:
                toAdd.append(repository)

    context = {"added": added, "toAdd": toAdd}
    return render(request, "misc/add-repo.html", context)


@login_required
def show_repo(request, pk):
    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    context = {"repo": repo}
    return render(request, "misc/show-repo.html", context)


@login_required
def artifacts(request, pk):
    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    filtering = request.GET.get("filter")
    sorting = request.GET.get("sort")
    kwargs = {"run__workflow__repo": repo}
    if filtering == "expired-only":
        kwargs["expired"] = True
    if filtering == "active-only":
        kwargs["expired"] = False

    order = ["-created_at"]
    if sorting == "created_at" or sorting == "-created_at":
        order = [sorting]
    if sorting == "size_in_bytes" or sorting == "-size_in_bytes":
        order = [sorting, "-created_at"]

    context = {
        "repo": repo,
        "artifacts": Artifact.objects.filter(**kwargs).order_by(*order),
        "number": Artifact.objects.filter(
            run__workflow__repo=repo, expired=False
        ).count(),
        "size": Artifact.objects.filter(
            run__workflow__repo=repo, expired=False
        ).aggregate(Sum("size_in_bytes")),
    }
    return render(request, "misc/artifacts.html", context)


@login_required
def download(request, pk):
    artifact = get_object_or_404(
        Artifact, pk=pk, run__workflow__repo__user=request.user
    )
    res = requests.get(artifact.download, headers=request_headers(request.user))
    res.raise_for_status()
    response = HttpResponse(res.content, content_type=res.headers["Content-Type"])
    response["Content-Disposition"] = res.headers["Content-Disposition"]
    return response


@login_required
def delete(request, pk):
    artifact = get_object_or_404(
        Artifact, pk=pk, run__workflow__repo__user=request.user
    )
    repo = artifact.run.workflow.repo
    res = requests.delete(
        "https://api.github.com/repos/%s/actions/artifacts/%s"
        % (repo.nwo, artifact.artifact_id),
        headers=request_headers(request.user),
    )
    res.raise_for_status()
    artifact.delete()
    return redirect("/artifacts/%s?msg=artifact-deleted" % repo.id)


@login_required
def runs(request, pk):
    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    filtering = request.GET.get("filter")
    sorting = request.GET.get("sort")
    order = ["-start_time"]
    if sorting == "start_time" or sorting == "-start_time":
        order = [sorting]
    if sorting == "elapsed" or sorting == "-elapsed":
        order = [sorting, "-start_time"]

    kwargs = {"workflow__repo": repo}
    if filtering == "failed-only":
        kwargs["conclusion"] = "failure"

    context = {
        "repo": repo,
        "runs": Run.objects.filter(**kwargs).order_by(*order)
    }
    for run in context["runs"]:
        run.total_artifact_size = Artifact.objects.filter(run=run).aggregate(
            Sum("size_in_bytes")
        )["size_in_bytes__sum"]

    return render(request, "misc/runs.html", context)

@login_required
def workflow(request, pk):
    workflow = get_object_or_404(Workflow, id=pk, repo__user=request.user)
    context = {
        "workflow": workflow,
        "states": Run.objects.values('conclusion').distinct().annotate(Count('conclusion')),
        "artifact_count": Artifact.objects.filter(run__workflow=workflow, expired=False).count(),
        "artifact_size": Artifact.objects.filter(run__workflow=workflow, expired=False).aggregate(Sum("size_in_bytes")),
        "run_count": Run.objects.filter(workflow=workflow).count(),
        "elapsed_time_sum": Run.objects.filter(workflow=workflow).aggregate(Sum('elapsed'))["elapsed__sum"],
        "elapsed_time_avg": Run.objects.filter(workflow=workflow).aggregate(Avg('elapsed'))["elapsed__avg"],
    }
    return render(request, "misc/workflow.html", context)

@login_required
def workflows(request, pk):
    workflows = Workflow.objects.filter(repo__id=pk, repo__user=request.user)
    context = {"workflows": workflows}
    return render(request, "misc/workflows.html", context)