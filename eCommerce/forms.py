"""Forms vendors use to create and edit stores and products."""
from django import forms

from .models import Product, Store


class StoreForm(forms.ModelForm):
    """Form for creating or editing a store."""

    class Meta:
        """Use the Store model's name and description fields."""

        model = Store
        fields = ["name", "description"]


class ProductForm(forms.ModelForm):
    """Form for adding or editing a product."""

    class Meta:
        """Use the Product model's fields, except the store."""

        model = Product
        fields = ["name", "description", "price", "stock"]
