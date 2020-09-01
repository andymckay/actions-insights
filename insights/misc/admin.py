from django.contrib import admin

from .models import Repo, Workflow, Token, Run, Artifact

admin.site.register(Repo)
admin.site.register(Workflow)
admin.site.register(Token)
admin.site.register(Run)
admin.site.register(Artifact)
