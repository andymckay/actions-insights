from django.urls import path

from . import importer, views, login

urlpatterns = [
    path("", views.index, name="index"),
    path("logout", login.logout_view, name="logout_view"),
    path("oauth/redirect", login.oauth, name="oauth"),
    path("add-repo", views.add_repo, name="add-repo"),
    path("show-repo/<int:pk>", views.show_repo, name="show-repo"),
    path("import-repo/<int:pk>", importer.import_repo, name="import-repo"),
    path("workflows/<int:pk>", views.workflows, name="workflows"),
    path("workflows/workflow/<int:pk>", views.workflow, name="workflow"),
    path("artifacts/<int:pk>", views.artifacts, name="artifacts"),
    path("artifacts/download/<int:pk>", views.download, name="download"),
    path("artifacts/delete/<int:pk>", views.delete, name="delete"),
    path("runs/<int:pk>", views.runs, name="runs"),
]
