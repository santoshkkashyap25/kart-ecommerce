import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with dummy products using static images'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Ensure media directory exists
        media_product_dir = os.path.join(settings.MEDIA_ROOT, 'productimg')
        if not os.path.exists(media_product_dir):
            os.makedirs(media_product_dir, exist_ok=True)
            
        static_img_dir = os.path.join(settings.BASE_DIR, 'app', 'static', 'app', 'images', 'product')
        
        products_data = [
            # Mobiles
            {'title': 'iPhone 14 Pro', 'selling_price': 120000, 'discounted_price': 110000, 'brand': 'Apple', 'category': 'M', 'img': 'M1.jpg', 'sku': 'IPH14P'},
            {'title': 'Samsung S23 Ultra', 'selling_price': 110000, 'discounted_price': 95000, 'brand': 'Samsung', 'category': 'M', 'img': 'M2.jpg', 'sku': 'S23U'},
            {'title': 'OnePlus 11', 'selling_price': 60000, 'discounted_price': 55000, 'brand': 'OnePlus', 'category': 'M', 'img': 'M3.jpg', 'sku': 'OP11'},
            {'title': 'Google Pixel 7', 'selling_price': 50000, 'discounted_price': 45000, 'brand': 'Google', 'category': 'M', 'img': 'M4.jpg', 'sku': 'PIX7'},
            {'title': 'Redmi Note 12', 'selling_price': 20000, 'discounted_price': 18000, 'brand': 'Xiaomi', 'category': 'M', 'img': 'M5.jpg', 'sku': 'REDN12'},
            
            # Laptops
            {'title': 'MacBook Pro 16', 'selling_price': 220000, 'discounted_price': 199999, 'brand': 'Apple', 'category': 'L', 'img': 'M1.jpg', 'sku': 'MBP16'},
            {'title': 'Dell XPS 15', 'selling_price': 160000, 'discounted_price': 145000, 'brand': 'Dell', 'category': 'L', 'img': 'M2.jpg', 'sku': 'XPS15'},
            {'title': 'HP Spectre x360', 'selling_price': 130000, 'discounted_price': 120000, 'brand': 'HP', 'category': 'L', 'img': 'M3.jpg', 'sku': 'HPSPEC'},
            {'title': 'Lenovo ThinkPad X1', 'selling_price': 140000, 'discounted_price': 128000, 'brand': 'Lenovo', 'category': 'L', 'img': 'M4.jpg', 'sku': 'TPX1'},

            # Headphones
            {'title': 'Sony WH-1000XM5', 'selling_price': 30000, 'discounted_price': 27000, 'brand': 'Sony', 'category': 'H', 'img': 'H1.jpg', 'sku': 'SONYXM5'},
            {'title': 'Bose QuietComfort 45', 'selling_price': 25000, 'discounted_price': 22000, 'brand': 'Bose', 'category': 'H', 'img': 'H2.jpg', 'sku': 'BOSE45'},
            {'title': 'AirPods Max', 'selling_price': 55000, 'discounted_price': 52000, 'brand': 'Apple', 'category': 'H', 'img': 'H3.jpg', 'sku': 'AIRMAX'},
            {'title': 'JBL Tune 760NC', 'selling_price': 6000, 'discounted_price': 5000, 'brand': 'JBL', 'category': 'H', 'img': 'H4.jpg', 'sku': 'JBL760'},
            
            # Watches
            {'title': 'Apple Watch Series 8', 'selling_price': 45000, 'discounted_price': 42000, 'brand': 'Apple', 'category': 'W', 'img': 'W1.jpg', 'sku': 'AW8'},
            {'title': 'Samsung Galaxy Watch 5', 'selling_price': 28000, 'discounted_price': 25000, 'brand': 'Samsung', 'category': 'W', 'img': 'W2.jpg', 'sku': 'GW5'},
            {'title': 'Fossil Gen 6', 'selling_price': 22000, 'discounted_price': 18000, 'brand': 'Fossil', 'category': 'W', 'img': 'W3.jpg', 'sku': 'FOSS6'},
            {'title': 'Amazfit GTR 4', 'selling_price': 15000, 'discounted_price': 13000, 'brand': 'Amazfit', 'category': 'W', 'img': 'W4.jpg', 'sku': 'AMZ4'},
        ]
        
        for p_data in products_data:
            img_name = p_data.pop('img')
            sku = p_data['sku']
            src_path = os.path.join(static_img_dir, img_name)
            dst_path = os.path.join(media_product_dir, img_name)
            
            # Copy image from static to media if it exists
            if os.path.exists(src_path):
                shutil.copy(src_path, dst_path)
            
            # Create product
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    **p_data,
                    'product_image': f'productimg/{img_name}', 
                    'stock_quantity': 50, 
                    'description': f'This is a premium {p_data["title"]} from {p_data["brand"]}.'
                }
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with dummy products'))
