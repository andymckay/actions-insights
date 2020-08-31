from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("logout", views.logout_view, name="logout_view"),
    path("oauth/redirect", views.oauth, name="oauth"),
]
