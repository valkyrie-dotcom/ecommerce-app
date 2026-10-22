"""Views for the eCommerce app: products, reviews, stores, cart,
checkout, the web API and the Reddit feed."""
import smtplib

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import ProductForm, StoreForm
from .functions.reddit import get_reddit_posts
from .models import Order, OrderItem, Product, Review, Store
from .serializers import ProductSerializer, ReviewSerializer, StoreSerializer
from .utils import build_invoice_email


# ---------- Products ----------

@login_required
def list_products(request):
    """Show all products to users who may view them."""
    if not request.user.has_perm("eCommerce.view_products"):
        return render(request, "eCommerce/products_list.html", {
            "error": "You do not have permission to view products."
        })
    products = Product.objects.all()
    return render(
        request, "eCommerce/products_list.html", {"products": products}
    )


@login_required
def view_product_page(request):
    """Find a product by name (search form or product link) and show it
    with its reviews."""
    user = request.user
    if user.has_perm("eCommerce.view_products"):
        # The name comes from the search form (POST) or a product link (GET)
        product_name = (
            request.POST.get("product") or request.GET.get("product")
        )

        if request.method == "POST" or product_name:
            if not product_name:
                return render(request, "eCommerce/product_page.html", {
                    "error": "No product name was given."
                })

            try:
                product = Product.objects.get(name=product_name)
                return render(
                    request, "eCommerce/product_page.html",
                    {"product": product},
                )
            except ObjectDoesNotExist:
                return render(request, "eCommerce/product_page.html", {
                    "error": "Product not found."
                })

        return render(request, "eCommerce/product_page.html")

    return render(request, "eCommerce/product_page.html", {
        "error": "You do not have permission to view this product."
    })


def get_rating(value):
    """Return the rating as a whole number from 1 to 5, or None if the
    value is not a valid rating."""
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None
    if 1 <= rating <= 5:
        return rating
    return None


@login_required
def leave_review(request):
    """Save a buyer's rating and review for a product."""
    user = request.user
    if not user.has_perm("eCommerce.add_review"):
        return render(request, "eCommerce/product_page.html", {
            "error": "Only buyers can leave reviews."
        })
    if request.method == "POST":
        product = get_object_or_404(Product, pk=request.POST.get("product"))
        comment = request.POST.get("comment", "").strip()
        rating = get_rating(request.POST.get("rating"))

        if rating is None or not comment:
            return render(request, "eCommerce/product_page.html", {
                "product": product,
                "error": "Please choose a rating from 1 to 5 and write a "
                         "comment.",
            })

        # Verified if the user has bought this product before
        verified = OrderItem.objects.filter(
            order__buyer=user, product=product
        ).exists()
        Review.objects.create(
            product=product, user=user, rating=rating,
            comment=comment, verified=verified,
        )
        return render(
            request, "eCommerce/product_page.html", {"product": product}
        )
    return redirect("eCommerce:product_page")


# ---------- Vendors and stores (buyers and vendors) ----------

@login_required
def vendor_list(request):
    """Show each vendor with the stores listed under them."""
    if not request.user.has_perm("eCommerce.view_products"):
        return render(request, "eCommerce/vendor_list.html", {
            "error": "You do not have permission to view vendors."
        })
    # Only users who own at least one store are vendors with stores
    vendors = (
        get_user_model().objects.filter(store__isnull=False)
        .distinct().order_by("username")
    )
    return render(
        request, "eCommerce/vendor_list.html", {"vendors": vendors}
    )


@login_required
def store_list(request):
    """Show all stores and the vendor of each one."""
    if not request.user.has_perm("eCommerce.view_products"):
        return render(request, "eCommerce/store_list.html", {
            "error": "You do not have permission to view stores."
        })
    stores = Store.objects.select_related("owner").order_by("name")
    return render(request, "eCommerce/store_list.html", {"stores": stores})


@login_required
def store_products(request, pk):
    """Show the products of one store, using the product catalogue
    page."""
    if not request.user.has_perm("eCommerce.view_products"):
        return render(request, "eCommerce/products_list.html", {
            "error": "You do not have permission to view products."
        })
    store = get_object_or_404(Store, pk=pk)
    return render(request, "eCommerce/products_list.html", {
        "store": store,
        "products": store.products.all(),
    })


# ---------- Vendors: stores ----------

@login_required
def my_stores(request):
    """Show a vendor's stores and their products."""
    if not request.user.has_perm("eCommerce.view_store"):
        return render(request, "eCommerce/my_stores.html", {
            "error": "Only vendors can view stores."
        })
    stores = Store.objects.filter(owner=request.user)
    return render(request, "eCommerce/my_stores.html", {"stores": stores})


@login_required
def create_store(request):
    """Let a vendor create a store."""
    if not request.user.has_perm("eCommerce.add_store"):
        return render(request, "eCommerce/store_form.html", {
            "error": "Only vendors can create stores."
        })
    form = StoreForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        store = form.save(commit=False)
        store.owner = request.user
        store.save()
        return redirect("eCommerce:my_stores")
    return render(request, "eCommerce/store_form.html", {"form": form})


@login_required
def edit_store(request, pk):
    """Let a vendor edit one of their own stores."""
    if not request.user.has_perm("eCommerce.change_store"):
        return render(request, "eCommerce/store_form.html", {
            "error": "You do not have permission to edit stores."
        })
    # Vendors can only edit their own stores
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    form = StoreForm(request.POST or None, instance=store)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("eCommerce:my_stores")
    return render(request, "eCommerce/store_form.html", {"form": form})


@login_required
def delete_store(request, pk):
    """Let a vendor remove one of their own stores."""
    if not request.user.has_perm("eCommerce.delete_store"):
        return render(request, "eCommerce/my_stores.html", {
            "error": "You do not have permission to remove stores."
        })
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == "POST":
        store.delete()
    return redirect("eCommerce:my_stores")


@login_required
def store_reviews(request, pk):
    """Show a vendor all the reviews of the products in one of their
    stores."""
    if not request.user.has_perm("eCommerce.view_store"):
        return render(request, "eCommerce/store_reviews.html", {
            "error": "Only vendors can view store reviews."
        })
    # Vendors can only see the reviews of their own stores
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    reviews = (
        Review.objects.filter(product__store=store)
        .select_related("product", "user")
        .order_by("product__name")
    )
    return render(request, "eCommerce/store_reviews.html", {
        "store": store,
        "reviews": reviews,
    })


# ---------- Vendors: products ----------

@login_required
def add_product(request, store_pk):
    """Let a vendor add a product to one of their own stores."""
    if not request.user.has_perm("eCommerce.add_products"):
        return render(request, "eCommerce/product_form.html", {
            "error": "You do not have permission to add products."
        })
    store = get_object_or_404(Store, pk=store_pk, owner=request.user)
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.store = store
        product.save()
        return redirect("eCommerce:my_stores")
    return render(request, "eCommerce/product_form.html", {"form": form})


@login_required
def edit_product(request, pk):
    """Let a vendor edit a product in one of their own stores."""
    if not request.user.has_perm("eCommerce.change_products"):
        return render(request, "eCommerce/product_form.html", {
            "error": "You do not have permission to edit products."
        })
    product = get_object_or_404(Product, pk=pk, store__owner=request.user)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("eCommerce:my_stores")
    return render(request, "eCommerce/product_form.html", {"form": form})


@login_required
def delete_product(request, pk):
    """Let a vendor remove a product from one of their own stores."""
    if not request.user.has_perm("eCommerce.delete_products"):
        return render(request, "eCommerce/my_stores.html", {
            "error": "You do not have permission to remove products."
        })
    product = get_object_or_404(Product, pk=pk, store__owner=request.user)
    if request.method == "POST":
        product.delete()
    return redirect("eCommerce:my_stores")


# ---------- Buyers: cart and checkout ----------

@login_required
def add_item_to_cart(request):
    """Add a quantity of a product to the buyer's cart in the session,
    without going over the stock available."""
    if not request.user.has_perm("eCommerce.add_order"):
        return render(request, "eCommerce/main_cart_page.html", {
            "error": "Only buyers can use a cart."
        })
    # The cart stores product ids, because two stores can sell
    # products with the same name
    item = request.POST.get("item")
    quantity = request.POST.get("quantity")

    if not item or not quantity:
        return redirect("eCommerce:main_cart_page")

    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    try:
        product = Product.objects.get(pk=item)
    except (Product.DoesNotExist, ValueError):
        messages.error(request, "That product could not be found.")
        return redirect("eCommerce:main_cart_page")

    # The cart can never hold more than the stock available
    cart = request.session.get("cart", {})
    new_quantity = cart.get(item, 0) + quantity
    if new_quantity > product.stock:
        messages.error(
            request,
            f"Only {product.stock} of {product.name} in stock. "
            f"You already have {cart.get(item, 0)} in your cart.",
        )
        return redirect("eCommerce:main_cart_page")

    cart[item] = new_quantity
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("eCommerce:main_cart_page")


def retrieve_products(request):
    """Return the products and quantities in the session cart."""
    products = []
    session = request.session
    if "cart" in session:
        for product_id, quantity in session["cart"].items():
            try:
                product = Product.objects.get(pk=product_id)
                products.append({"product": product, "quantity": quantity})
            except Product.DoesNotExist:
                pass
    return products


@login_required
def show_user_cart(request):
    """Show the buyer's cart with subtotals and the total price."""
    if not request.user.has_perm("eCommerce.add_order"):
        return render(request, "eCommerce/main_cart_page.html", {
            "error": "Only buyers can use a cart."
        })
    cart_items = retrieve_products(request)
    total_price = 0
    for item in cart_items:
        subtotal = item["product"].price * item["quantity"]
        item["subtotal"] = subtotal
        total_price += subtotal
    return render(request, "eCommerce/main_cart_page.html", {
        "cart": cart_items,
        "total_price": total_price,
    })


@login_required
def clear_cart(request):
    """Empty the buyer's cart."""
    request.session["cart"] = {}
    request.session.modified = True
    return redirect("eCommerce:main_cart_page")


@login_required
def checkout(request):
    """Save the order, reduce the stock, email the invoice and empty the
    cart."""
    user = request.user
    if not user.has_perm("eCommerce.add_order"):
        return render(request, "eCommerce/main_cart_page.html", {
            "error": "Only buyers can check out."
        })
    cart_items = retrieve_products(request)
    if request.method != "POST" or not cart_items:
        return redirect("eCommerce:main_cart_page")

    # Check the stock again, in case someone else bought it first
    for item in cart_items:
        product = item["product"]
        if item["quantity"] > product.stock:
            messages.error(
                request,
                f"Only {product.stock} of {product.name} left in stock. "
                f"Please clear your cart and add it again.",
            )
            return redirect("eCommerce:main_cart_page")

    # Save the order and reduce the stock together, so either both
    # happen or neither does
    with transaction.atomic():
        order = Order.objects.create(buyer=user)
        for item in cart_items:
            product = item["product"]
            OrderItem.objects.create(
                order=order, product=product, quantity=item["quantity"]
            )
            product.stock -= item["quantity"]
            product.save()

    # Email invoice to buyer. If the email fails the order is still saved.
    try:
        build_invoice_email(order).send()
    except (smtplib.SMTPException, OSError):
        messages.error(
            request, "Your order was placed, but the invoice email could "
                     "not be sent."
        )

    # Remove products from cart
    request.session["cart"] = {}
    request.session.modified = True

    return render(
        request, "eCommerce/checkout_complete.html", {"order": order}
    )


# ---------- API ----------

@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def view_vendor_stores(request, vendor_id):
    """Return the stores listed under one vendor."""
    stores = Store.objects.filter(owner_id=vendor_id)
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def view_store_products(request, store_id):
    """Return the products of one store."""
    store = get_object_or_404(Store, pk=store_id)
    serializer = ProductSerializer(store.products.all(), many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def view_product_reviews(request, product_id):
    """Return the reviews of one product."""
    product = get_object_or_404(Product, pk=product_id)
    serializer = ReviewSerializer(product.reviews.all(), many=True)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_add_store(request):
    """Let a vendor create a store for themselves."""
    if not request.user.has_perm("eCommerce.add_store"):
        return Response({"error": "Only vendors can create stores."},
                        status=status.HTTP_403_FORBIDDEN)

    # Vendors can only create stores for themselves
    owner_id = request.data.get("owner")
    if owner_id is None:
        return Response({"error": "Owner field is required."},
                        status=status.HTTP_400_BAD_REQUEST)
    if int(owner_id) != request.user.id:
        return Response({"error": "User ID and owner ID do not match."},
                        status=status.HTTP_403_FORBIDDEN)

    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_add_product(request):
    """Let a vendor add a product to one of their own stores."""
    if not request.user.has_perm("eCommerce.add_products"):
        return Response({"error": "Only vendors can add products."},
                        status=status.HTTP_403_FORBIDDEN)

    # Vendors can only add products to their own stores
    store_id = request.data.get("store")
    if store_id is None:
        return Response({"error": "Store field is required."},
                        status=status.HTTP_400_BAD_REQUEST)
    store = get_object_or_404(Store, pk=store_id)
    if store.owner != request.user:
        return Response({"error": "You can only add products to your "
                                  "own stores."},
                        status=status.HTTP_403_FORBIDDEN)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Reddit feed ----------

def reddit_feed(request):
    """Show posts from the r/django subreddit."""
    # Call our helper function to fetch posts
    posts = get_reddit_posts("django")

    # Pass the posts into the template
    return render(request, "eCommerce/reddit_feed.html", {"posts": posts})
