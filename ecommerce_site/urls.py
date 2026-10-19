"""Root URL configuration for the ecommerce_site project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Login, registration and password reset live at the site root
    path("", include("grabsomore.urls")),
    # The shop itself lives under /ecommerce/
    path("ecommerce/", include("eCommerce.urls")),
]
