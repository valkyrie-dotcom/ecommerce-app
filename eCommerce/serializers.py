"""Serializers that turn stores, products and reviews into JSON for the
web API."""
from rest_framework import serializers

from .models import Product, Review, Store


class StoreSerializer(serializers.ModelSerializer):
    """Convert a Store to and from JSON."""

    class Meta:
        """Use the Store model and these fields."""

        model = Store
        fields = ["id", "owner", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):
    """Convert a Product to and from JSON."""

    class Meta:
        """Use the Product model and these fields."""

        model = Product
        fields = ["id", "store", "name", "description", "price", "stock"]


class ReviewSerializer(serializers.ModelSerializer):
    """Convert a Review to JSON."""

    class Meta:
        """Use the Review model and these fields."""

        model = Review
        fields = ["id", "product", "user", "rating", "comment", "verified"]
