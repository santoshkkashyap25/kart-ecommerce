from django.views import View
from django.contrib import messages
from django.db.models import Q, Avg, Count, Case, When
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils import timezone
from .models import *
from .forms import *
import json
import csv
from django.http import HttpResponse

class ProductView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
        
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        watches = Product.objects.filter(category='W')
        headphones = Product.objects.filter(category='H')
        
        recently_viewed = []
        viewed_ids = request.session.get('recently_viewed', [])
        if viewed_ids:
            recently_viewed = Product.objects.filter(id__in=viewed_ids)

        return render(request, 'app/home.html', {
            'mobiles': mobiles,
            'laptops': laptops,
            'watches': watches,
            'headphones': headphones,
            'recently_viewed': recently_viewed,
            'totalitem': totalitem
        })

from django.contrib.auth import logout

def user_logout(request):
    """Log out user on both GET and POST requests, then redirect to login"""
    logout(request)
    return redirect('login')

@login_required 
def add_to_cart(request):
    user = request.user
    if request.method == 'POST':
        product_id = request.POST.get('prod_id')
    else:
        product_id = request.GET.get('prod_id')
        
    product = get_object_or_404(Product, id=product_id)
    
    # Check if item already in cart to avoid duplicates or update quantity
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('showcart') 

def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).select_related('product')
        totalitem = cart.count()
        
        amount = 0.0
        shipping_amount = 70.0
        
        if cart.exists():
            for p in cart:
                amount += (p.quantity * float(p.product.discounted_price))
            
            total_amount = amount + shipping_amount
            return render(request, 'app/addtocart.html', {
                'carts': cart,
                'total_amount': total_amount,
                'amount': amount,
                'totalitem': totalitem
            })
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem})
    return redirect('login')

@login_required
def plus_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        user = request.user
        c = get_object_or_404(Cart, product_id=prod_id, user=user)
        c.quantity += 1
        c.save()
        
        cart_items = Cart.objects.filter(user=user).select_related('product')
        amount = sum(p.quantity * float(p.product.discounted_price) for p in cart_items)
        shipping_amount = 70.0

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def minus_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        user = request.user
        c = get_object_or_404(Cart, product_id=prod_id, user=user)
        
        if c.quantity > 1:
            c.quantity -= 1
            c.save()
            
        cart_items = Cart.objects.filter(user=user).select_related('product')
        amount = sum(p.quantity * float(p.product.discounted_price) for p in cart_items)
        shipping_amount = 70.0

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        user = request.user
        Cart.objects.filter(user=user, product_id=prod_id).delete()
        
        cart_items = Cart.objects.filter(user=user).select_related('product')
        totalitem = cart_items.count()
        
        if cart_items.exists():
            amount = sum(p.quantity * float(p.product.discounted_price) for p in cart_items)
            shipping_amount = 70.0
            total_amount = amount + shipping_amount

            data = {
                'status': 'success',
                'amount': amount,
                'total_amount': total_amount,
            }
        else:
            empty_html = render_to_string('app/emptycart_message.html', {'totalitem': totalitem})
            data = {
                'status': 'empty',
                'html': empty_html,
            }
        
        return JsonResponse(data)


@login_required # as it is function based
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',{'add':add,'active': 'btn-primary'})

@login_required # as it is function based
def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request,'app/orders.html',{'order_placed':op})

# Maps for display
category_name_map = {
    'M': 'Mobile',
    'L': 'Laptop',
    'W': 'Watch',
    'H': 'Headphone',
}

price_map = {
    'M': 10000,
    'L': 50000,
    'W': 5000,
    'H': 2000,
}

def category_view(request, category, filter_type='all'):
    category = category.upper()  # normalize category to uppercase

    # Ensure category exists
    if category not in category_name_map:
        raise Http404("Category does not exist")

    products = Product.objects.filter(category=category)

    # Filter by price
    if filter_type == 'below':
        products = products.filter(discounted_price__lt=price_map[category])
    elif filter_type == 'above':
        products = products.filter(discounted_price__gte=price_map[category])

    context = {
        'category_name': category_name_map[category],
        'products': products,
        'filter_type': filter_type,
        'all_url': f"/{category.lower()}",
        'below_url': f"/{category.lower()}/below",
        'above_url': f"/{category.lower()}/above",
        'below_price': price_map.get(category),
    }
    return render(request, 'app/category.html', context)


class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request,'app/customerregistration.html',
            {'form':form})
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Successfully Registered')
            form.save()
        return render(request,'app/customerregistration.html',

            {'form':form})

@login_required
def checkout(request):
    user = request.user
    addresses = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user).select_related('product')
    
    amount = 0.0
    shipping_amount = 70.0
    total_amount = 0.0
    
    if cart_items.exists():
        amount = sum(p.quantity * float(p.product.discounted_price) for p in cart_items)
        total_amount = amount + shipping_amount
        
    return render(request, 'app/checkout.html', {
        'add': addresses,
        'total_amount': total_amount,
        'cart_items': cart_items
    })

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    # SECURITY: Ensure customer belongs to this user
    customer = get_object_or_404(Customer, id=custid, user=user)
    cart = Cart.objects.filter(user=user)
    
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})
        
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            
            # Use update_or_create or filter logic to avoid duplicate Customer profiles
            # Or just create a new one as the UI seems to allow multiple addresses
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Profile address added successfully!')
            return redirect('address')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})



# ============= WISHLIST FEATURE =============
@login_required
def add_to_wishlist(request):
    """Add product to user's wishlist"""
    if request.method == 'POST' or request.method == 'GET':
        data_source = request.POST if request.method == 'POST' else request.GET
        prod_id = data_source.get('prod_id')
        product = get_object_or_404(Product, id=prod_id)
        user = request.user
        
        # Check if already in wishlist
        wishlist_item = Wishlist.objects.filter(user=user, product=product)
        if wishlist_item.exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'info', 'message': 'Already in wishlist'})
            messages.info(request, 'Product already in wishlist')
        else:
            Wishlist.objects.create(user=user, product=product)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Added to wishlist'})
            messages.success(request, 'Product added to wishlist')
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def show_wishlist(request):
    """Display user's wishlist"""
    user = request.user
    wishlist = Wishlist.objects.filter(user=user).select_related('product')
    totalitem = Cart.objects.filter(user=user).count() if user.is_authenticated else 0
    
    return render(request, 'app/wishlist.html', {
        'wishlist': wishlist,
        'totalitem': totalitem
    })


@login_required
def remove_from_wishlist(request):
    """Remove product from wishlist"""
    source = request.POST if request.method == 'POST' else request.GET
    prod_id = source.get('prod_id')
    Wishlist.objects.filter(user=request.user, product_id=prod_id).delete()
    return JsonResponse({'status': 'success'})


# ============= PRODUCT REVIEW FEATURE =============
@login_required
def add_review(request, pk):
    """Add review for a product"""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, 'Please provide both rating and comment')
            return redirect('product-detail', pk=pk)
            
        # Check if user already reviewed
        existing_review = Review.objects.filter(user=request.user, product=product)
        if existing_review.exists():
            messages.warning(request, 'You have already reviewed this product')
        else:
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Review submitted successfully')
        
        return redirect('product-detail', pk=pk)


# ============= ADVANCED SEARCH & FILTER =============
class ProductSearchView(View):
    """Advanced product search with filters"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        sort_by = request.GET.get('sort', 'newest')
        
        products = Product.objects.all()
        
        # Search by title, description, or brand
        if query:
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query)
            )
        
        # Filter by category
        if category:
            products = products.filter(category=category)
        
        # Filter by price range
        if min_price:
            products = products.filter(discounted_price__gte=min_price)
        if max_price:
            products = products.filter(discounted_price__lte=max_price)
        
        # Sorting
        if sort_by == 'price_low':
            products = products.order_by('discounted_price')
        elif sort_by == 'price_high':
            products = products.order_by('-discounted_price')
        elif sort_by == 'popular':
            products = products.annotate(
                order_count=Count('orderplaced')
            ).order_by('-order_count')
        else:  # newest
            products = products.order_by('-id')
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
        
        context = {
            'products': page_obj,
            'query': query,
            'category': category,
            'totalitem': totalitem,
            'total_results': products.count()
        }
        
        return render(request, 'app/search_results.html', context)


# ============= PRODUCT RECOMMENDATIONS =============
def get_recommended_products(user, product=None, limit=4):
    """Get personalized product recommendations"""
    
    if product:
        # Related products from same category and brand
        related = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).order_by('?')[:limit]
        return related
    
    if user.is_authenticated:
        # Get user's order history
        ordered_products = OrderPlaced.objects.filter(
            user=user
        ).values_list('product__category', flat=True)
        
        if ordered_products:
            # Recommend from categories user has ordered from
            recommended = Product.objects.filter(
                category__in=ordered_products
            ).order_by('?')[:limit]
            return recommended
    
    # Default: Popular products
    return Product.objects.annotate(
        order_count=Count('orderplaced')
    ).order_by('-order_count')[:limit]


# ============= ENHANCED PRODUCT DETAIL =============
class ProductDetailView(View):
    """Product detail with reviews and recommendations"""
    
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        reviews = Review.objects.filter(product=product).select_related('user')
        
        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        rating_distribution = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
        
        # Check if in wishlist
        in_wishlist = False
        item_already_in_cart = False
        totalitem = 0
        
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            in_wishlist = Wishlist.objects.filter(
                user=request.user, product=product
            ).exists()
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)
            ).exists()
        
        # Track recently viewed product
        add_to_recently_viewed(request, pk)
        
        # Get recommendations
        recommended_products = get_recommended_products(request.user, product)
        
        # Get related products (same category)
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        
        context = {
            'product': product,
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'total_reviews': reviews.count(),
            'rating_distribution': rating_distribution,
            'in_wishlist': in_wishlist,
            'item_already_in_cart': item_already_in_cart,
            'totalitem': totalitem,
            'recommended_products': recommended_products,
            'related_products': related_products,
        }
        
        return render(request, 'app/productdetail.html', context)


# ============= ORDER TRACKING =============
@login_required
def track_order(request, order_id):
    """Track order status with timeline"""
    order = get_object_or_404(OrderPlaced, id=order_id, user=request.user)
    
    # Order status timeline
    status_timeline = [
        {'status': 'Accepted', 'completed': order.status in ['Accepted', 'Packed', 'On The Way', 'Delivered']},
        {'status': 'Packed', 'completed': order.status in ['Packed', 'On The Way', 'Delivered']},
        {'status': 'On The Way', 'completed': order.status in ['On The Way', 'Delivered']},
        {'status': 'Delivered', 'completed': order.status == 'Delivered'},
    ]
    
    totalitem = Cart.objects.filter(user=request.user).count()
    
    return render(request, 'app/track_order.html', {
        'order': order,
        'status_timeline': status_timeline,
        'totalitem': totalitem
    })


# ============= CANCEL ORDER =============
@login_required
def cancel_order(request, order_id):
    """Cancel an order if not yet shipped"""
    order = get_object_or_404(OrderPlaced, id=order_id, user=request.user)
    
    if order.status in ['Accepted', 'Pending']:
        order.status = 'Cancel'
        order.save()
        messages.success(request, 'Order cancelled successfully')
    else:
        messages.error(request, 'Order cannot be cancelled at this stage')
    
    return redirect('orders')


# ============= RECENTLY VIEWED PRODUCTS =============
def add_to_recently_viewed(request, product_id):
    """Track recently viewed products in session"""
    recently_viewed = request.session.get('recently_viewed', [])
    
    if product_id in recently_viewed:
        recently_viewed.remove(product_id)
    
    recently_viewed.insert(0, product_id)
    recently_viewed = recently_viewed[:10]  # Keep only last 10

    # Save only if it actually changed
    if request.session.get('recently_viewed') != recently_viewed:
        request.session['recently_viewed'] = recently_viewed
        request.session.modified = True


@login_required
def show_recently_viewed(request):
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if recently_viewed_ids:
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(recently_viewed_ids)])
        products = Product.objects.filter(id__in=recently_viewed_ids).order_by(preserved)
    else:
        products = Product.objects.none()
    
    totalitem = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    
    return render(request, 'app/recently_viewed.html', {
        'products': products,
        'totalitem': totalitem
    })


# ============= PRODUCT QUICK VIEW (AJAX) =============
def product_quick_view(request, pk):
    """Quick view product details in modal"""
    product = get_object_or_404(Product, pk=pk)
    
    data = {
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'selling_price': product.selling_price,
        'discounted_price': product.discounted_price,
        'brand': product.brand,
        'image_url': product.product_image.url if product.product_image else '',
    }
    
    return JsonResponse(data)


# ============= EXPORT ORDER HISTORY =============
@login_required
def export_order_history(request):
    """Export order history as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="order_history.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Quantity', 'Price', 'Status', 'Date'])
    
    orders = OrderPlaced.objects.filter(user=request.user).select_related('product')
    
    for order in orders:
        writer.writerow([
            order.id,
            order.product.title,
            order.quantity,
            order.total_cost,
            order.status,
            order.ordered_date.strftime('%Y-%m-%d')
        ])
    
    return response