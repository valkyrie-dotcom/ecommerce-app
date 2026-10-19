"""App configuration for the eCommerce app."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_groups(sender, **kwargs):
    """Create the Vendors and Buyers groups with their permissions."""
    from django.contrib.auth.models import Group, Permission

    permissions = {
        "Vendors": [
            "add_store", "change_store", "delete_store", "view_store",
            "add_products", "change_products", "delete_products",
            "view_products",
        ],
        "Buyers": ["view_products", "add_order", "add_review"],
    }
    for group_name, codenames in permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        group.permissions.set(Permission.objects.filter(
            content_type__app_label="eCommerce", codename__in=codenames
        ))


class EcommerceConfig(AppConfig):
    """Configuration for the eCommerce app."""

    name = "eCommerce"

    def ready(self):
        """Create the groups each time migrations finish."""
        post_migrate.connect(create_groups, sender=self)
