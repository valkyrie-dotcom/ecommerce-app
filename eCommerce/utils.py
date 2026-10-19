"""Helper functions for the eCommerce app."""
from django.core.mail import EmailMessage


def build_invoice_email(order):
    """Create the invoice email for an order and return it unsent."""
    subject = f"Invoice for order {order.pk}"
    body = f"Hi {order.buyer.username},\nHere is your invoice:\n\n"
    for item in order.items.all():
        body += (
            f"{item.product.name} x {item.quantity}: R{item.subtotal()}\n"
        )
    body += f"\nTotal: R{order.total()}"
    return EmailMessage(subject, body, to=[order.buyer.email])
