import datetime
import json

import requests

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from github import Github
from django.contrib.auth.models import User

from misc.models import Artifact, Repo, Run, Token, Timing, Workflow
from misc.utils import get_access_token_for_user, request_headers

MAX_PAGES = 100

class Log():
    def __init__(self):
        self.data = []

    def append(self, string):
        string = "%s: %s" % (datetime.datetime.now(), string)
        print(string)
        self.data.append(string)


def get_workflows(log, repo, repo_from_api, k):
    workflows = repo_from_api.get_workflows().get_page(k)
    if not workflows:
        log.append("No workflows for page: %s, stopping" % k)
        return

    log.append("Found workflows in page: %s" % k)
    for workflow_from_api in workflows:
        workflow = Workflow.objects.get_or_create(
            workflow_id=workflow_from_api.id, repo=repo
        )[0]
        workflow.name = workflow_from_api.name
        workflow.path = workflow_from_api.path.split("/")[-1]
        workflow.save()
        log.append("Saved workflow: %s" % workflow.path)

    k += 1
    if k > MAX_PAGES:
        log.append("Aborting workflow import at %s pages" % k)
        return

    get_workflows(log, repo, repo_from_api, k)

def get_runs(log, workflow, workflow_from_api, k):
    runs = workflow_from_api.get_runs().get_page(k)
    if not runs:
        log.append("No runs for page: %s, stopping" % k)
        return

    log.append("Found runs in page: %s" % k)
    for run_from_api in runs:
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

            timing_from_api = run_from_api.timing()
            print(timing_from_api.billable)
            if timing_from_api.billable:
                for key, value in timing_from_api.billable.items():
                    timing = Timing.objects.get_or_create(os=key, run=run)[0]
                    timing.length = value["total_ms"]
                    timing.jobs = value["jobs"]
                    timing.save()
                    log.append("Saved timing for run: %s" % run.id)
            else:
                log.append("Timing billing empty for run: %s" % run.id)

    k += 1
    if k > MAX_PAGES:
        log.append("Aborting runs import at %s pages" % k)
        return

    get_runs(log, workflow, workflow_from_api, k)


def get_artifacts(log, repo, run, access, k):
    res = requests.get(
        "https://api.github.com/repos/%s/actions/runs/%s/artifacts?page=%s"
        % (repo.nwo, run.run_id, k),
        headers={
            "Authorization": "token %s" % access,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    res.raise_for_status()
    data = res.json()
    if not data["artifacts"]:
        log.append("No artifacts found for page: %s, stopping" % k)
        return

    log.append("Found artifacts in page: %s" % k)
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

    k += 1
    if k > MAX_PAGES:
        log.append("Aborting artifact import at %s pages" % k)
        return

    get_artifacts(log, repo, run, access, k)

@login_required
def import_repo(request, pk):
    log = Log()
    log.append("Starting run.")
    access = get_access_token_for_user(request.user)
    log.append("Getting access token for user: %s" % request.user)
    g = Github(access)

    repo = get_object_or_404(Repo, pk=pk, user=request.user)
    log.append("Got repo: %s" % repo.nwo)
    repo_from_api = g.get_repo(repo.nwo)
    repo.public = not repo_from_api.private
    repo.save()

    get_workflows(log, repo, repo_from_api, 0)

    for workflow in Workflow.objects.filter(repo=repo):
        workflow_from_api = repo_from_api.get_workflow(str(workflow.workflow_id))
        get_runs(log, workflow, workflow_from_api, 0)
        for run in Run.objects.filter(workflow_id=workflow.id):
            # PyGithub uses Python syntax, first page is 0.
            # Looks like the REST API starts with the first page at 1.
            get_artifacts(log, repo, run, access, 1)

    context = {"log": log.data, "repo": repo}
    return render(request, "misc/import-repo.html", context)

@csrf_exempt
def webhook(request):
    log = Log()
    data = json.loads(request.body)
    if data["action"] == "requested":
        log.append("Ignoring a webhook with action: requested.")
        return HttpResponse()

    if data["action"] == "completed":
        username = data["sender"]["login"]
        workflow_id = data["workflow"]["id"]
        run_id = data["workflow_run"]["id"]
        nwo = data["repository"]["full_name"]

        try:
            user = User.objects.get(username='github:%s' % username)
        except ObjectDoesNotExist:
            log.append("Event sender was %s and that doesn't exist in this database, ignoring.")
            return HttpResponse()

        # This is all wrong and needs fixing up.
        access = get_access_token_for_user(user)
        g = Github(access)
        repo_from_api = g.get_repo(nwo)
        repo = Repo.objects.get(nwo=nwo)

        workflow_from_api = repo_from_api.get_workflow(str(workflow_id))
        # We don't create a workflow if one doesn't exist :(
        workflow = Workflow.objects.get(workflow_id=workflow_from_api.id)

        # There is no get_run? Damn
        res = requests.get(
            "https://api.github.com/repos/%s/actions/runs/%s"
            % (repo.nwo, run_id),
            headers=request_headers(user)
        )
        res.raise_for_status()
        run_from_api = res.json()

        # Perhaps we should populate a Run object in PyGithub to make this easier?
        run = Run.objects.get_or_create(
            run_id=run_from_api["id"], workflow_id=workflow.id
        )[0]
        run.conclusion = run_from_api["conclusion"]
        run.start_time = datetime.datetime.strptime(
            run_from_api["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        run.end_time = datetime.datetime.strptime(
            run_from_api["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        run.elapsed = run.end_time - run.start_time
        run.status = run_from_api["status"]
        run.save()
        log.append("Saved run: %s" % run.id)

        # PyGithub uses Python syntax, first page is 0.
        # Looks like the REST API starts with the first page at 1.
        get_artifacts(log, repo, run, access, 1)

    return HttpResponse()