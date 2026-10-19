"""Register the grabsomore models with the Django admin."""
from django.contrib import admin

from .models import ResetToken

admin.site.register(ResetToken)
