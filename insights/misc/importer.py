import datetime

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from github import Github

from misc.models import Artifact, Repo, Run, Token, Workflow


@login_required
def import_repo(request, pk):
    access = Token.objects.all()[0].access
    log = []
    log.append("Getting access.")
    g = Github(access)

    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    log.append("Got repo: %s" % repo.nwo)
    repo_from_api = g.get_repo(repo.nwo)
    repo.public = not repo_from_api.private
    repo.save()

    for workflow_from_api in repo_from_api.get_workflows().get_page(0):
        workflow = Workflow.objects.get_or_create(
            workflow_id=workflow_from_api.id, repo=repo
        )[0]
        workflow.name = workflow_from_api.name
        workflow.path = workflow_from_api.path.split("/")[-1]
        workflow.save()
        log.append("Saved workflow: %s" % workflow.path)

    for workflow in Workflow.objects.filter(repo=repo):
        workflow_from_api = repo_from_api.get_workflow(str(workflow.workflow_id))
        for run_from_api in workflow_from_api.get_runs():
            if run_from_api.status == "completed":
                run = Run.objects.get_or_create(
                    run_id=run_from_api.id, workflow_id=workflow.id
                )[0]
                run.conclusion = run_from_api.conclusion
                run.start_time = run_from_api.created_at
                run.end_time = run_from_api.updated_at
                run.elapsed = run_from_api.updated_at - run_from_api.created_at
                run.status = run_from_api.status
                run.save()
                log.append("Saved run: %s" % run.id)

        for run in Run.objects.filter(workflow_id=workflow.id):
            res = requests.get(
                "https://api.github.com/repos/%s/actions/runs/%s/artifacts"
                % (repo.nwo, run.run_id),
                headers={
                    "Authorization": "token %s" % access,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            res.raise_for_status()
            data = res.json()
            for artifact_from_api in data["artifacts"]:
                artifact = Artifact.objects.get_or_create(
                    artifact_id=artifact_from_api["id"], run=run
                )[0]
                artifact.created_at = datetime.datetime.strptime(
                    artifact_from_api["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
                artifact.expired = artifact_from_api["expired"]
                artifact.size_in_bytes = artifact_from_api["size_in_bytes"]
                artifact.name = artifact_from_api["name"]

                artifact.download = artifact_from_api["archive_download_url"]
                artifact.save()
                log.append("Artifact saved %s" % artifact.id)

    context = {"log": log, "repo": repo}
    return render(request, "misc/import-repo.html", context)
