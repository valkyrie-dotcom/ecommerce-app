"""URL patterns for the grabsomore (accounts) app."""
from django.urls import path

from . import views

app_name = "grabsomore"

urlpatterns = [
    # Default page: login form
    path("", views.login_user, name="login"),
    path("register/", views.register_user, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("welcome/", views.welcome, name="welcome"),

    # Password reset
    path(
        "request-password-reset/",
        views.send_password_reset, name="request_password_reset",
    ),
    path(
        "reset/<str:token>/",
        views.reset_user_password, name="password_reset_form",
    ),
    path("reset_password/", views.reset_password, name="reset_password"),
]
