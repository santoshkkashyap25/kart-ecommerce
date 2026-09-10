from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils import timezone

# Create your models here.

STATE_CHOICES = (
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Delhi', 'Delhi'),
    ('Puducherry', 'Puducherry'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh')
)

class Customer(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	locality = models.CharField(max_length=255)
	city = models.CharField(max_length=60)
	zipcode = models.IntegerField()
	state=models.CharField(choices=STATE_CHOICES,max_length=60)

	def __str__(self):
		return f"{self.name} ({self.id})"

CATEGORY_CHOICES = (
    ('M', 'Mobile'),
    ('L', 'Laptop'),
    ('W', 'Watches'),
    ('H', 'Headphones'),
)

class Product(models.Model):
    title = models.CharField(max_length=255)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=5)
    product_image = models.ImageField(upload_to='productimg')

    stock_quantity = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    specifications = models.JSONField(default=dict, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    weight = models.FloatField(default=0, help_text="Weight in kg")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def discount_percent(self):
        if self.selling_price > 0:
            return round(((self.selling_price - self.discounted_price) / self.selling_price) * 100)
        return 0


    def __str__(self):
        return f"{self.title} ({self.id})"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Cart: {self.user.username} - {self.product.title}"

    @property
    def total_cost(self):
        return self.quantity*self.product.discounted_price
    

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
)

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,default='Pending')

    def __str__(self):
        return f"Order {self.id}: {self.user.username}"


    @property
    def total_cost(self):
        return self.quantity*self.product.discounted_price
    

class Wishlist(models.Model):
    """User's wishlist for saving products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class Review(models.Model):
    """Product reviews and ratings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.rating}★)"


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    email_verified = models.BooleanField(default=False)
    newsletter_subscribed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class ProductImage(models.Model):
    """Multiple images for a product"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='productimg/gallery/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"{self.product.title} - Image"


class ProductQuestion(models.Model):
    """Customer questions about products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(max_length=300)
    answer = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Q: {self.question[:50]}"


class NewsletterSubscription(models.Model):
    """Newsletter subscriptions"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Contact form messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class ShippingMethod(models.Model):
    """Different shipping options"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(help_text="Estimated delivery days")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - Rs.{self.price}"


class OrderTracking(models.Model):
    """Track order status changes"""
    order = models.ForeignKey('OrderPlaced', on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Order {self.order.id} - {self.status}"


class RecentlyViewed(models.Model):
    """Track recently viewed products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.username} viewed {self.product.title}"


class ProductNotification(models.Model):
    """Notify users when product is back in stock"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class FlashSale(models.Model):
    """Flash sales / limited time offers"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_quantity = models.IntegerField(default=100)
    sold_quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Flash Sale - {self.product.title}"
    
    def is_live(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_time <= now <= self.end_time and
            self.sold_quantity < self.max_quantity
        )





class UserNotification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = (
        ('order', 'Order Update'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
        ('review', 'Review'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

