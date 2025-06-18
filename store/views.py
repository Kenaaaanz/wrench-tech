import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, Vendor
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm, VendorRegistrationForm, ProductForm, VendorShippingStatusForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.urls import reverse
from django.template.loader import get_template, TemplateDoesNotExist
from django.http import HttpResponse
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.mpesa_utils import generate_timestamp, generate_password
from .models import Address, Cart, Order
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt






# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    if not address_id:
        # Optionally, handle missing address_id (redirect or show error)
        return redirect('store:cart')  # or your cart page

    address = get_object_or_404(Address, id=address_id, user=user)
    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        Order.objects.create(
            user=user,
            address=address,
            product=item.product,
            quantity=item.quantity
        )
        item.delete()
    return redirect('store:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')



def vendor_landing(request):
    return render(request, 'store/vendor_landing.html')


def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in as a vendor.")
            return redirect(reverse('store:login') + '?next=/vendor/dashboard/')
    else:
        form = VendorRegistrationForm()
    return render(request, 'store/vendor_register.html', {'form': form})

@login_required
def vendor_dashboard(request):
    try:
        vendor = request.user.vendor_profile
    except Vendor.DoesNotExist:
        return redirect('store:vendor_register')

    products = Product.objects.filter(vendor=vendor)
    orders = Order.objects.filter(product__vendor=vendor).select_related('product', 'user')

    # Calculate today's earnings
    today = timezone.now().date()
    todays_earnings = (
        Order.objects.filter(
            product__vendor=vendor,
            ordered_date__date=today
        ).aggregate(total=Sum('product__price'))
    )
    total_today = todays_earnings['total'] or 0

    return render(request, 'store/vendor_dashboard.html', {
        'vendor': vendor,
        'products': products,
        'orders': orders,
        'total_today': total_today,
    })

@login_required
def vendor_products(request):
    vendor = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'store/vendor_products.html', {'products': products})

@login_required
def vendor_add_product(request):
    vendor = request.user.vendor_profile
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()
            return redirect('store:vendor_products')
    else:
        form = ProductForm()
    return render(request, 'store/vendor_product_form.html', {'form': form})

@login_required
def vendor_edit_product(request, pk):
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, pk=pk, vendor=vendor)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store:vendor_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/vendor_product_form.html', {'form': form})

@login_required
def vendor_delete_product(request, pk):
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, pk=pk, vendor=vendor)
    if request.method == 'POST':
        product.delete()
        return redirect('store:vendor_products')
    return render(request, 'store/vendor_product_confirm_delete.html', {'product': product})

@login_required
def vendor_update_order_status(request, pk):
    vendor = request.user.vendor_profile
    order = get_object_or_404(Order, pk=pk, product__vendor=vendor)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, 'store/vendor_update_order_status.html', {'order': order})

@login_required
def vendor_orders(request):
    vendor = request.user.vendor_profile
    orders = Order.objects.filter(product__vendor=vendor).select_related('product', 'user')
    return render(request, 'store/vendor_orders.html', {'orders': orders})

def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        form = VendorShippingStatusForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_detail', vendor_id=vendor.id)
    else:
        form = VendorShippingStatusForm(instance=vendor)
    return render(request, 'vendor_detail.html', {'vendor': vendor, 'form': form})

def debug_template(request):
    try:
        get_template('store/vendor_dashboard.html')
        return HttpResponse("Template found!")
    except TemplateDoesNotExist as e:
        return HttpResponse(f"Template not found! {e.args}")
    
def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    return r.json()['access_token']

@csrf_exempt
def mpesa_stk_push(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")
        timestamp = generate_timestamp()
        password = generate_password(settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY, timestamp)
        access_token = get_mpesa_access_token()
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "Order",
            "TransactionDesc": "Order Payment"
        }
        print("STK Push Payload:", payload)
        response = requests.post(api_url, json=payload, headers=headers)
        print("STK Push API Response:", response.text)  # Log the full response
        return JsonResponse(response.json())
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def mpesa_callback(request):
    # Handle the callback data here
    # For now, just return a simple response
    return HttpResponse("MPESA callback received", status=200)

@login_required
def vendor_stats(request):
    vendor = request.user.vendor_profile

    # Daily
    daily = (
        Order.objects.filter(product__vendor=vendor)
        .annotate(period=TruncDay('ordered_date'))
        .values('period')
        .annotate(total=Sum('product__price'))
        .order_by('period')
    )

    # Weekly
    weekly = (
        Order.objects.filter(product__vendor=vendor)
        .annotate(period=TruncWeek('ordered_date'))
        .values('period')
        .annotate(total=Sum('product__price'))
        .order_by('period')
    )

    # Monthly
    monthly = (
        Order.objects.filter(product__vendor=vendor)
        .annotate(period=TruncMonth('ordered_date'))
        .values('period')
        .annotate(total=Sum('product__price'))
        .order_by('period')
    )

    # Yearly
    yearly = (
        Order.objects.filter(product__vendor=vendor)
        .annotate(period=TruncYear('ordered_date'))
        .values('period')
        .annotate(total=Sum('product__price'))
        .order_by('period')
    )

    context = {
        'daily': list(daily),
        'weekly': list(weekly),
        'monthly': list(monthly),
        'yearly': list(yearly),
    }
    return render(request, 'store/vendor_stats.html', context)

@login_required
def vendor_detailed_stats(request):
    vendor = request.user.vendor_profile
    # Query for detailed stats and transaction history
    # Example: orders = Order.objects.filter(product__vendor=vendor).select_related('product')
    return render(request, 'store/vendor_detailed_stats.html', {
        'vendor': vendor,
        # 'orders': orders,
        # Add more context as needed
    })


@login_required
@require_POST
def vendor_update_order_status_ajax(request, pk):
    vendor = request.user.vendor_profile
    order = get_object_or_404(Order, pk=pk, product__vendor=vendor)
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        return JsonResponse({'success': True, 'new_status': order.get_status_display()})
    return JsonResponse({'success': False, 'error': 'Invalid status'})



