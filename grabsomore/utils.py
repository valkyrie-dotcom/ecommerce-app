"""Helper functions for password reset links and emails."""
import secrets
from datetime import timedelta
from hashlib import sha1

from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone

from .models import ResetToken


def generate_reset_url(user):
    """Create a reset URL with a token that expires in 5 minutes."""
    domain = "http://127.0.0.1:8000"
    token = secrets.token_urlsafe(16)
    expiry_date = timezone.now() + timedelta(minutes=5)

    # Save the hashed token, and put the raw token in the URL
    ResetToken.objects.create(
        user=user,
        token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date,
    )
    return domain + reverse("grabsomore:password_reset_form", args=[token])


def build_email(user, reset_url):
    """Create the password reset email."""
    subject = "Password Reset"
    body = (
        f"Hi {user.username},\n"
        f"Here is your link to reset your password:\n"
        f"{reset_url}"
    )
    return EmailMessage(subject, body, to=[user.email])
