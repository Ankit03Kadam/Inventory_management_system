from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# class login_(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=100)
#     email = models.CharField(max_length=100)
#     password = models.CharField(max_length=50)
    
#     def __str__(self):
#         return self.username
    
class Supplier(models.Model):
    # Supplier Information
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE) 
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, unique=True, default="unknown@example.com")
    phone = models.CharField(max_length=20, blank=True)

    # Address Information
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    zip_postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    # Customer Information
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE) 
    Customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    customer_Img = models.ImageField(upload_to='images/',null=True,default='customer_default.jpeg',blank=True)
    email = models.EmailField(max_length=254, null=True,unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Billing Address
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    zip_postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    product_Img = models.ImageField(upload_to='images/',default='default.png',blank=True,null=True)
    sku = models.CharField(max_length=50, unique=True,default="DEFAULT-SKU")
    category = models.CharField(max_length=50, blank=True, null=True)
    current_stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    supplier = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Stock(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE) 
    stock_id = models.AutoField(primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(User, null=True,on_delete=models.CASCADE) 
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField(default=timezone.now)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='Pending') # e.g., 'Pending', 'Shipped', 'Delivered'

    def __str__(self):
        return f"Order #{self.id} for {self.customer.name if self.customer else 'N/A'}"

class OrderItem(models.Model):
    user = models.ForeignKey(User, null=True,on_delete=models.CASCADE) 
    # Links this item to a specific Order
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # Links this item to a specific Product
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
class SalesDetail(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE) 
    sales_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.sales_id} - {self.product.name}"


class Purchase(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE) 
    purchase_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase {self.purchase_id} - {self.supplier.name}"


class PurchaseDetail(models.Model):
    user = models.ForeignKey(User, null=True,on_delete=models.CASCADE) 
    purchase_detail_id = models.AutoField(primary_key=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_cost = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase Detail {self.purchase_detail_id} - {self.product.name}"


# class CustomUser(AbstractUser):
#     pass2