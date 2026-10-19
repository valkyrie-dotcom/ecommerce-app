"""Database models for the eCommerce app: stores, products, orders and
reviews."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Store(models.Model):
    """A store owned by a vendor."""

    # Vendor who owns the store
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return the store's name."""
        return self.name


class Product(models.Model):
    """A product sold by a store, with its price and stock level."""

    # Store that sells this product
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=100)  # Product name
    description = models.TextField(blank=True)  # Optional description
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()  # Qty available

    def __str__(self):
        """Return the product's name."""
        return self.name

    class Meta:
        """Extra permissions used by the Vendors and Buyers groups."""

        permissions = [
            ("add_products", "Can add products"),
            ("change_products", "Can change products"),
            ("delete_products", "Can delete products"),
            ("view_products", "Can view products"),
        ]


class Order(models.Model):
    """An order created when a buyer checks out."""

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total(self):
        """Return the total price of all items in the order."""
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        """Return the order number."""
        return f"Order {self.pk}"


class OrderItem(models.Model):
    """One product and its quantity in an order."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def subtotal(self):
        """Return the price of this item times its quantity."""
        return self.product.price * self.quantity


class Review(models.Model):
    """A buyer's review of a product, with a rating from 1 to 5."""

    RATING_CHOICES = [(number, str(number)) for number in range(1, 6)]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField()
    # True when reviewer has bought this product
    verified = models.BooleanField(default=False)

    def __str__(self):
        """Return which product the review is for and who wrote it."""
        return f"Review of {self.product.name} by {self.user.username}"
