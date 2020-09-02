from django.contrib import admin

from .models import Artifact, Repo, Run, Token, Timing, Workflow

admin.site.register(Repo)
admin.site.register(Workflow)
admin.site.register(Token)
admin.site.register(Run)
admin.site.register(Artifact)
admin.site.register(Timing)
