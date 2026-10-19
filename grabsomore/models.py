"""Database models for the grabsomore (accounts) app."""
from django.conf import settings
from django.db import models


class ResetToken(models.Model):
    """A hashed password reset token that expires after 5 minutes."""

    # Reference to the user who requested the password reset
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    # The token is stored hashed
    token = models.CharField(max_length=500)
    # When this token expires
    expiry_date = models.DateTimeField()
    # Whether this token has already been used
    used = models.BooleanField(default=False)

    def __str__(self):
        """Return the token's user and whether it has been used."""
        return f"ResetToken(user={self.user.username}, used={self.used})"
