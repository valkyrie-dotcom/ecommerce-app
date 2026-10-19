"""URL patterns for the eCommerce app."""
from django.urls import path

from . import views

app_name = "eCommerce"

urlpatterns = [
    # Products
    path("", views.list_products, name="products_list"),
    path("product/", views.view_product_page, name="product_page"),
    path("review/", views.leave_review, name="leave_review"),

    # Vendors: stores and products
    path("my-stores/", views.my_stores, name="my_stores"),
    path("stores/new/", views.create_store, name="create_store"),
    path("stores/<int:pk>/edit/", views.edit_store, name="edit_store"),
    path("stores/<int:pk>/delete/", views.delete_store, name="delete_store"),
    path(
        "stores/<int:store_pk>/add-product/",
        views.add_product, name="add_product",
    ),
    path("product/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path(
        "product/<int:pk>/delete/",
        views.delete_product, name="delete_product",
    ),

    # Buyers: cart and checkout
    path("add-to-cart/", views.add_item_to_cart, name="add_to_cart"),
    path("cart/", views.show_user_cart, name="main_cart_page"),
    path("clear-cart/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
]
