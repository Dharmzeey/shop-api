import csv
from products.models import Category, Brand, Product
import random
from django.core.files import File

def run():
  f = open("utilities/products.csv")
  reader = csv.reader(f)
  next(reader)
  
  for row in reader:
    randon_no = random.randint(1,13)
    media_name = f"utilities/images/{randon_no}.jpg"
    category, created = Category.objects.get_or_create(name=row[0])
    brand, created = Brand.objects.get_or_create(category=category, name=row[1])
    with open(media_name, 'rb') as image_file:
      product, created = Product.objects.get_or_create(
        category=category,
        brand=brand,
        name=row[2],
        description=row[3],
        price=row[4],
        image = File(image_file, name=f'{randon_no}.jpg'),
        stock=row[5],
        availability_status=row[6],
        utilization_status=row[7]
      )
