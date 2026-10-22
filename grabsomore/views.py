"""Views for the grabsomore app: login, registration, logout and
password reset."""
from hashlib import sha1

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import (
    MultipleObjectsReturned, ObjectDoesNotExist, ValidationError,
)
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import ResetToken
from .utils import build_email, generate_reset_url


def login_user(request):
    """Log a user in with their username and password."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session.set_expiry(3600)  # Session lasts one hour
            return HttpResponseRedirect(reverse("grabsomore:welcome"))
        return render(
            request, "grabsomore/login.html", {"error": "Invalid credentials"}
        )
    return render(request, "grabsomore/login.html")


def register_user(request):
    """Register a new buyer or vendor and add them to their group."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")
        password_conf = request.POST.get("password_conf")
        email = request.POST.get("email", "").strip()
        account_type = request.POST.get("account_type")

        # Check the input before creating the user
        if not username:
            return render(request, "grabsomore/register.html", {
                "error": "Please enter a username."
            })
        if User.objects.filter(username=username).exists():
            return render(request, "grabsomore/register.html", {
                "error": "That username is already taken."
            })
        # Each email address can only be used once, so password resets
        # and invoices go to the right person
        if not email:
            return render(request, "grabsomore/register.html", {
                "error": "Please enter an email address."
            })
        if User.objects.filter(email__iexact=email).exists():
            return render(request, "grabsomore/register.html", {
                "error": "An account with that email address already "
                         "exists."
            })
        if not password:
            return render(request, "grabsomore/register.html", {
                "error": "Please enter a password."
            })
        if password != password_conf:
            return render(request, "grabsomore/register.html", {
                "error": "Passwords do not match."
            })
        # Django's built-in password validators (set in settings.py)
        try:
            validate_password(password, User(username=username))
        except ValidationError as error:
            return render(request, "grabsomore/register.html", {
                "error": " ".join(error.messages)
            })

        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        # Add the user to the group for their account type
        group_name = "Vendors" if account_type == "vendor" else "Buyers"
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            pass

        user.save()
        login(request, user)
        return redirect(reverse("grabsomore:welcome"))
    return render(request, "grabsomore/register.html")


def change_user_password(username, new_password):
    """Set a new (hashed) password for the user with this username."""
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()


def logout_user(request):
    """Log the user out and go back to the login page."""
    logout(request)
    return HttpResponseRedirect(reverse("grabsomore:login"))


@login_required
def welcome(request):
    """Show the welcome page after logging in."""
    return render(request, "grabsomore/welcome.html")


def send_password_reset(request):
    """Email a password reset link to the user with this email address."""
    if request.method == "POST":
        user_email = request.POST.get("email", "").strip()
        try:
            user = User.objects.get(email__iexact=user_email)
            reset_url = generate_reset_url(user)
            email = build_email(user, reset_url)
            email.send()
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            pass  # Show the same page so no account details are revealed
        return render(
            request, "grabsomore/reset_email_sent.html", {"email": user_email}
        )
    return render(request, "grabsomore/request_password_reset.html")


def reset_user_password(request, token):
    """Check the token from the emailed link and show the new password
    form."""
    hashed_token = sha1(token.encode()).hexdigest()
    try:
        user_token = ResetToken.objects.get(token=hashed_token)
    except ResetToken.DoesNotExist:
        return render(request, "grabsomore/password_reset_invalid.html")

    # Check if the token has expired
    if user_token.expiry_date < timezone.now():
        user_token.delete()
        return render(request, "grabsomore/password_reset_expired.html")

    # Save the username and token in the session for the next step
    request.session["user"] = user_token.user.username
    request.session["token"] = token
    return render(request, "grabsomore/password_reset.html")


def reset_password(request):
    """Set the new password if the passwords match, are strong enough and
    the token is still valid."""
    if request.method == "POST":
        username = request.session.get("user")
        token = request.session.get("token")
        password = request.POST.get("password")
        password_conf = request.POST.get("password_conf")

        if not username or not token:
            return render(request, "grabsomore/password_reset_invalid.html")

        if not password:
            return render(request, "grabsomore/password_reset.html", {
                "error": "Please enter a password."
            })
        if password != password_conf:
            return render(request, "grabsomore/password_reset.html", {
                "error": "Passwords do not match."
            })
        # Django's built-in password validators (set in settings.py)
        try:
            validate_password(password, User(username=username))
        except ValidationError as error:
            return render(request, "grabsomore/password_reset.html", {
                "error": " ".join(error.messages)
            })

        try:
            hashed_token = sha1(token.encode()).hexdigest()
            reset_token = ResetToken.objects.get(token=hashed_token)
        except ResetToken.DoesNotExist:
            return render(request, "grabsomore/password_reset_invalid.html")

        # Check the token again in case it expired while on the page
        if reset_token.expiry_date < timezone.now():
            reset_token.delete()
            return render(request, "grabsomore/password_reset_expired.html")

        change_user_password(username, password)

        # Delete the token so it cannot be used again
        reset_token.delete()
        request.session.flush()
        return HttpResponseRedirect(reverse("grabsomore:login"))

    return HttpResponseRedirect(reverse("grabsomore:login"))
