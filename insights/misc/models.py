from django.db import models
from django.contrib.auth.models import User

class GitHubRepo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Workflow(models.Model):
    repo = models.ForeignKey(GitHubRepo, on_delete=models.CASCADE)
    workflow_id = models.IntegerField()
    workflow_name = models.CharField(max_length=200)