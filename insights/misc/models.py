from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access = models.CharField(max_length=255)


class Repo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nwo = models.CharField(max_length=200, default="")
    access_token = models.CharField(max_length=255, default="")
    public = models.BooleanField(default=True)


class Workflow(models.Model):
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    workflow_id = models.IntegerField()
    name = models.CharField(max_length=200, default="")
    path = models.CharField(max_length=200, default="")


class Run(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    run_id = models.IntegerField()
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    elapsed = models.DurationField(null=True)
    timing = models.IntegerField(default=0)
    status = models.TextField(max_length=200, default="")
    conclusion = models.TextField(max_length=200, default="")


class Artifact(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    artifact_id = models.IntegerField()
    created_at = models.DateTimeField(null=True)
    size_in_bytes = models.IntegerField(null=True)
    name = models.TextField(max_length=200, default=True)
    expired = models.BooleanField(default=True)
    download = models.URLField()
