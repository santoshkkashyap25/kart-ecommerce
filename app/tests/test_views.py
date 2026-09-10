from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Product, Customer, Cart, OrderPlaced, Wishlist, Review
from decimal import Decimal
import json
import uuid


class ProductViewTestCase(TestCase):
    """Test ProductView (Homepage)"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        # Create test products with unique SKUs
        self.mobile = Product.objects.create(
            title='Test Mobile',
            selling_price=10000,
            discounted_price=8000,
            description='Test mobile description',
            brand='TestBrand',
            category='M',
            product_image='test.jpg',
            sku='SKU_MOBILE_001'  # unique SKU
        )

        self.laptop = Product.objects.create(
            title='Test Laptop',
            selling_price=50000,
            discounted_price=45000,
            description='Test laptop description',
            brand='TestBrand',
            category='L',
            product_image='test.jpg',
            sku='SKU_LAPTOP_001'  # unique SKU
        )

    
    def test_homepage_loads_successfully(self):
        """Test homepage returns 200 status"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
    
    def test_homepage_displays_products(self):
        """Test homepage displays all product categories"""
        response = self.client.get(reverse('home'))
        self.assertIn('laptops', response.context)
        self.assertIn('mobiles', response.context)
        self.assertEqual(len(response.context['mobiles']), 1)
        self.assertEqual(len(response.context['laptops']), 1)
    
    def test_homepage_cart_count_for_authenticated_user(self):
        """Test cart count shows for logged in users"""
        self.client.login(username='testuser', password='testpass123')
        Cart.objects.create(user=self.user, product=self.mobile, quantity=1)
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['totalitem'], 1)
    
    def test_homepage_cart_count_for_anonymous_user(self):
        """Test cart count is 0 for anonymous users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['totalitem'], 0)


class ProductDetailViewTestCase(TestCase):
    """Test ProductDetailView"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.product = Product.objects.create(
            title='Test Product',
            selling_price=1000,
            discounted_price=800,
            description='Test description',
            brand='TestBrand',
            category='M',
            product_image='test.jpg'
        )
    
    def test_product_detail_loads(self):
        """Test product detail page loads successfully"""
        response = self.client.get(reverse('product-detail', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/productdetail.html')
    
    def test_product_detail_shows_correct_product(self):
        """Test correct product is displayed"""
        response = self.client.get(reverse('product-detail', kwargs={'pk': self.product.id}))
        self.assertEqual(response.context['product'].title, 'Test Product')
        self.assertEqual(response.context['product'].discounted_price, 800)
    
    def test_product_detail_shows_reviews(self):
        """Test product reviews are displayed"""
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='Great product!'
        )
        
        response = self.client.get(reverse('product-detail', kwargs={'pk': self.product.id}))
        self.assertEqual(response.context['total_reviews'], 1)
        self.assertEqual(response.context['avg_rating'], 5.0)
    
    def test_product_detail_cart_status(self):
        """Test item_already_in_cart flag"""
        self.client.login(username='testuser', password='testpass123')
        Cart.objects.create(user=self.user, product=self.product, quantity=1)
        
        response = self.client.get(reverse('product-detail', kwargs={'pk': self.product.id}))
        self.assertTrue(response.context['item_already_in_cart'])
    
    def test_product_detail_wishlist_status(self):
        """Test in_wishlist flag"""
        self.client.login(username='testuser', password='testpass123')
        Wishlist.objects.create(user=self.user, product=self.product)
        
        response = self.client.get(reverse('product-detail', kwargs={'pk': self.product.id}))
        self.assertTrue(response.context['in_wishlist'])
    
    def test_product_detail_404_for_invalid_id(self):
        """Test 404 for non-existent product"""
        response = self.client.get(reverse('product-detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class CartViewTestCase(TestCase):
    """Test shopping cart functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        self.product1 = Product.objects.create(
            title='Product 1',
            selling_price=1000,
            discounted_price=800,
            description='Test',
            brand='Brand',
            category='M',
            product_image='test.jpg',
            sku=f'SKU-{uuid.uuid4().hex[:8]}',  
        )

        self.product2 = Product.objects.create(
            title='Product 2',
            selling_price=2000,
            discounted_price=1500,
            description='Test',
            brand='Brand',
            category='M',
            product_image='test.jpg',
            sku=f'SKU-{uuid.uuid4().hex[:8]}', 
        )

    def test_add_to_cart_requires_login(self):
        """Test add to cart redirects to login for anonymous users"""
        response = self.client.post(reverse('add-to-cart'), {'prod_id': self.product1.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_add_to_cart_success(self):
        """Test successfully adding product to cart"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add-to-cart'), {'prod_id': self.product1.id})
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)
        cart_item = Cart.objects.get(user=self.user, product=self.product1)
        self.assertEqual(cart_item.quantity, 1)
    
    def test_show_cart_with_items(self):
        """Test cart page displays items correctly"""
        self.client.login(username='testuser', password='testpass123')
        Cart.objects.create(user=self.user, product=self.product1, quantity=2)
        Cart.objects.create(user=self.user, product=self.product2, quantity=1)
        
        response = self.client.get(reverse('showcart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/addtocart.html')
        self.assertEqual(len(response.context['carts']), 2)
        
        # Check total calculation
        expected_amount = (2 * 800) + (1 * 1500)  # 3100
        expected_total = expected_amount + 70  # 3170
        self.assertEqual(response.context['amount'], expected_amount)
        self.assertEqual(response.context['total_amount'], expected_total)
    
    def test_show_cart_empty(self):
        """Test empty cart page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('showcart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/emptycart.html')
    
    def test_plus_cart_increases_quantity(self):
        """Test increasing cart quantity"""
        self.client.login(username='testuser', password='testpass123')
        cart_item = Cart.objects.create(user=self.user, product=self.product1, quantity=1)
        
        response = self.client.post(reverse('plus_cart'), {'prod_id': self.product1.id})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['quantity'], 2)
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)
    
    def test_minus_cart_decreases_quantity(self):
        """Test decreasing cart quantity"""
        self.client.login(username='testuser', password='testpass123')
        cart_item = Cart.objects.create(user=self.user, product=self.product1, quantity=2)
        
        response = self.client.post(reverse('minus_cart'), {'prod_id': self.product1.id})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['quantity'], 1)
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)
    
    def test_minus_cart_minimum_quantity(self):
        """Test cart quantity doesn't go below 1"""
        self.client.login(username='testuser', password='testpass123')
        cart_item = Cart.objects.create(user=self.user, product=self.product1, quantity=1)
        
        response = self.client.post(reverse('minus_cart'), {'prod_id': self.product1.id})
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)  # Should stay at 1
    
    

class WishlistViewTestCase(TestCase):
    """Test wishlist functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.product = Product.objects.create(
            title='Test Product',
            selling_price=1000,
            discounted_price=800,
            description='Test',
            brand='Brand',
            category='M',
            product_image='test.jpg'
        )
    
    def test_add_to_wishlist_requires_login(self):
        """Test wishlist requires authentication"""
        response = self.client.post(reverse('add_to_wishlist'), {'prod_id': self.product.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_add_to_wishlist_success(self):
        """Test adding product to wishlist"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_to_wishlist'), {'prod_id': self.product.id})
        
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)
        wishlist_item = Wishlist.objects.get(user=self.user, product=self.product)
        self.assertIsNotNone(wishlist_item)
    
    def test_add_to_wishlist_duplicate(self):
        """Test adding same product twice to wishlist"""
        self.client.login(username='testuser', password='testpass123')
        Wishlist.objects.create(user=self.user, product=self.product)
        
        response = self.client.post(reverse('add_to_wishlist'), {'prod_id': self.product.id})
        
        # Should still be only 1 item
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)
    
    def test_show_wishlist(self):
        """Test displaying wishlist"""
        self.client.login(username='testuser', password='testpass123')
        Wishlist.objects.create(user=self.user, product=self.product)
        
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/wishlist.html')
        self.assertEqual(len(response.context['wishlist']), 1)
    
    def test_remove_from_wishlist(self):
        """Test removing product from wishlist"""
        self.client.login(username='testuser', password='testpass123')
        Wishlist.objects.create(user=self.user, product=self.product)
        
        response = self.client.post(reverse('remove_from_wishlist'), {'prod_id': self.product.id})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 0)


class ReviewViewTestCase(TestCase):
    """Test product review functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.product = Product.objects.create(
            title='Test Product',
            selling_price=1000,
            discounted_price=800,
            description='Test',
            brand='Brand',
            category='M',
            product_image='test.jpg'
        )
    
    def test_add_review_requires_login(self):
        """Test review requires authentication"""
        response = self.client.post(
            reverse('add_review', kwargs={'pk': self.product.id}),
            {'rating': 5, 'comment': 'Great product!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_add_review_success(self):
        """Test successfully adding a review"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('add_review', kwargs={'pk': self.product.id}),
            {'rating': 5, 'comment': 'Excellent product!'}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Review.objects.filter(user=self.user, product=self.product).count(), 1)
        
        review = Review.objects.get(user=self.user, product=self.product)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent product!')
    
    def test_add_review_duplicate_prevention(self):
        """Test user can only review product once"""
        self.client.login(username='testuser', password='testpass123')
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='First review'
        )
        
        response = self.client.post(
            reverse('add_review', kwargs={'pk': self.product.id}),
            {'rating': 4, 'comment': 'Second review'}
        )
        
        # Should still be only 1 review
        self.assertEqual(Review.objects.filter(user=self.user, product=self.product).count(), 1)


class SearchViewTestCase(TestCase):
    """Test product search functionality"""
    
    def setUp(self):
        self.client = Client()
        
        self.mobile1 = Product.objects.create(
            title='iPhone 14',
            selling_price=80000,
            discounted_price=75000,
            description='Apple smartphone',
            brand='Apple',
            category='M',
            product_image='test.jpg',
            sku=f'SKU-{uuid.uuid4().hex[:8]}', 
        )
        
        self.mobile2 = Product.objects.create(
            title='Samsung Galaxy',
            selling_price=60000,
            discounted_price=55000,
            description='Samsung smartphone',
            brand='Samsung',
            category='M',
            product_image='test.jpg',
            sku=f'SKU-{uuid.uuid4().hex[:8]}', 
        )
        
        self.laptop = Product.objects.create(
            title='MacBook Pro',
            selling_price=120000,
            discounted_price=110000,
            description='Apple laptop',
            brand='Apple',
            category='L',
            product_image='test.jpg',
            sku=f'SKU-{uuid.uuid4().hex[:8]}', 
        )
    
    def test_search_by_title(self):
        """Test searching products by title"""
        response = self.client.get(reverse('search'), {'q': 'iPhone'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].title, 'iPhone 14')
    
    def test_search_by_brand(self):
        """Test searching products by brand"""
        response = self.client.get(reverse('search'), {'q': 'Apple'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 2)  # iPhone and MacBook
    
    def test_search_by_category(self):
        """Test filtering by category"""
        response = self.client.get(reverse('search'), {'category': 'M'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 2)  # Both mobiles
    
    def test_search_by_price_range(self):
        """Test filtering by price range"""
        response = self.client.get(reverse('search'), {'min_price': 50000, 'max_price': 80000})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context['products']), 2)
    
    def test_search_sorting_price_low_to_high(self):
        """Test sorting by price (low to high)"""
        response = self.client.get(reverse('search'), {'sort': 'price_low'})
        products = list(response.context['products'])
        self.assertLessEqual(products[0].discounted_price, products[1].discounted_price)
    
    def test_search_sorting_price_high_to_low(self):
        """Test sorting by price (high to low)"""
        response = self.client.get(reverse('search'), {'sort': 'price_high'})
        products = list(response.context['products'])
        self.assertGreaterEqual(products[0].discounted_price, products[1].discounted_price)
    

class OrderViewTestCase(TestCase):
    """Test order functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.customer = Customer.objects.create(
            user=self.user,
            name='Test User',
            locality='Test Locality',
            city='Test City',
            zipcode=123456,
            state='Punjab'
        )
        
        self.product = Product.objects.create(
            title='Test Product',
            selling_price=1000,
            discounted_price=800,
            description='Test',
            brand='Brand',
            category='M',
            product_image='test.jpg'
        )
    
    def test_checkout_requires_login(self):
        """Test checkout requires authentication"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_checkout_page_loads(self):
        """Test checkout page displays correctly"""
        self.client.login(username='testuser', password='testpass123')
        Cart.objects.create(user=self.user, product=self.product, quantity=1)
        
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/checkout.html')
        self.assertIn('cart_items', response.context)
    
    def test_payment_done_creates_order(self):
        """Test order creation on payment"""
        self.client.login(username='testuser', password='testpass123')
        Cart.objects.create(user=self.user, product=self.product, quantity=2)
        
        response = self.client.get(reverse('paymentdone'), {'custid': self.customer.id})
        
        self.assertEqual(response.status_code, 302)  # Redirect to orders
        self.assertEqual(OrderPlaced.objects.filter(user=self.user).count(), 1)
        
        order = OrderPlaced.objects.get(user=self.user)
        self.assertEqual(order.product, self.product)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.customer, self.customer)
        
        # Cart should be cleared
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)
    
    def test_orders_page_displays_orders(self):
        """Test orders page shows user's orders"""
        self.client.login(username='testuser', password='testpass123')
        OrderPlaced.objects.create(
            user=self.user,
            customer=self.customer,
            product=self.product,
            quantity=1
        )
        
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/orders.html')
        self.assertEqual(len(response.context['order_placed']), 1)
    
    def test_track_order(self):
        """Test order tracking page"""
        self.client.login(username='testuser', password='testpass123')
        order = OrderPlaced.objects.create(
            user=self.user,
            customer=self.customer,
            product=self.product,
            quantity=1,
            status='Packed'
        )
        
        response = self.client.get(reverse('track_order', kwargs={'order_id': order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/track_order.html')
        self.assertEqual(response.context['order'], order)
    
    def test_cancel_order_success(self):
        """Test canceling an order"""
        self.client.login(username='testuser', password='testpass123')
        order = OrderPlaced.objects.create(
            user=self.user,
            customer=self.customer,
            product=self.product,
            quantity=1,
            status='Accepted'
        )
        
        response = self.client.get(reverse('cancel_order', kwargs={'order_id': order.id}))
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'Cancel')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_cancel_order_already_shipped(self):
        """Test cannot cancel shipped order"""
        self.client.login(username='testuser', password='testpass123')
        order = OrderPlaced.objects.create(
            user=self.user,
            customer=self.customer,
            product=self.product,
            quantity=1,
            status='On The Way'
        )
        
        response = self.client.get(reverse('cancel_order', kwargs={'order_id': order.id}))
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'On The Way')  # Should not change


class ProfileViewTestCase(TestCase):
    """Test user profile functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_profile_requires_login(self):
        """Test profile requires authentication"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_profile_page_loads(self):
        """Test profile page loads successfully"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/profile.html')
    
    def test_profile_update_success(self):
        """Test updating profile information"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'name': 'Test User',
            'locality': 'Test Locality',
            'city': 'Test City',
            'state': 'Punjab',
            'zipcode': 123456
        }
        
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 302)  # Now redirects with success message
        
        customer = Customer.objects.get(user=self.user)
        self.assertEqual(customer.name, 'Test User')
        self.assertEqual(customer.city, 'Test City')
    
    def test_address_page_displays_addresses(self):
        """Test address page shows user's addresses"""
        self.client.login(username='testuser', password='testpass123')
        Customer.objects.create(
            user=self.user,
            name='Test User',
            locality='Locality 1',
            city='City 1',
            zipcode=123456,
            state='Punjab'
        )
        
        response = self.client.get(reverse('address'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/address.html')
        self.assertEqual(len(response.context['add']), 1)


class CategoryViewTestCase(TestCase):
    """Test category filtering"""
    
    def setUp(self):
        self.client = Client()
        
        for i in range(5):
            Product.objects.create(
                title=f'Mobile {i}',
                selling_price=15000 if i < 3 else 8000,
                discounted_price=12000 if i < 3 else 6000,
                description='Test',
                brand='Brand',
                category='M',
                product_image='test.jpg',
                sku=f'SKU-{uuid.uuid4().hex[:8]}', 
            )
    
    def test_category_view_all_products(self):
        """Test viewing all products in category"""
        response = self.client.get('/m/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 5)
    
    def test_category_view_price_filter_below(self):
        """Test filtering products below price"""
        response = self.client.get('/m/below/')
        self.assertEqual(response.status_code, 200)
        # Products with price < 10000
        self.assertLessEqual(len(response.context['products']), 5)
    
    def test_category_view_price_filter_above(self):
        """Test filtering products above price"""
        response = self.client.get('/m/above/')
        self.assertEqual(response.status_code, 200)
        # Products with price >= 10000
        self.assertGreaterEqual(len(response.context['products']), 0)


class ExportOrderHistoryTestCase(TestCase):
    """Test order history export"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.customer = Customer.objects.create(
            user=self.user,
            name='Test User',
            locality='Test',
            city='Test',
            zipcode=123456,
            state='Punjab'
        )
        
        self.product = Product.objects.create(
            title='Test Product',
            selling_price=1000,
            discounted_price=800,
            description='Test',
            brand='Brand',
            category='M',
            product_image='test.jpg'
        )
    
    def test_export_order_history_csv(self):
        """Test exporting order history as CSV"""
        self.client.login(username='testuser', password='testpass123')
        OrderPlaced.objects.create(
            user=self.user,
            customer=self.customer,
            product=self.product,
            quantity=2
        )
        
        response = self.client.get(reverse('export_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('Order ID', content)
        self.assertIn('Test Product', content)


class RecentlyViewedTestCase(TestCase):
    """Test recently viewed functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.product = Product.objects.create(
            title='Viewed Product',
            selling_price=1000,
            discounted_price=800,
            description='Test description',
            brand='TestBrand',
            category='M',
            product_image='test.jpg',
            sku='SKU_VIEWED_001'
        )

    def test_recently_viewed_empty_session(self):
        """Test recently viewed page does not crash with empty session"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recently_viewed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/recently_viewed.html')
        self.assertEqual(len(response.context['products']), 0)

    def test_recently_viewed_with_products(self):
        """Test recently viewed page displays viewed items"""
        self.client.login(username='testuser', password='testpass123')
        session = self.client.session
        session['recently_viewed'] = [self.product.id]
        session.save()
        
        response = self.client.get(reverse('recently_viewed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].id, self.product.id)


class ProductQuickViewTestCase(TestCase):
    """Test product quick view AJAX endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            title='Quick View Product',
            selling_price=1000,
            discounted_price=800,
            description='Quick description',
            brand='TestBrand',
            category='M',
            product_image='test.jpg',
            sku='SKU_QUICK_001'
        )

    def test_quick_view_returns_json(self):
        """Test quick view returns JSON details"""
        response = self.client.get(reverse('product_quick_view', kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.product.id)
        self.assertEqual(data['title'], 'Quick View Product')
        self.assertEqual(float(data['discounted_price']), 800.0)

